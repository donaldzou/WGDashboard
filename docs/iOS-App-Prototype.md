# iOS App Implementation Guide

This document walks through creating a SwiftUI prototype that talks to a WGDashboard server. The server exposes REST endpoints like `handshake`, `authenticate`, and `isTotpEnabled` which the app can call. Example definitions from `src/dashboard.py`:

```python
@app.route(f'{APP_PREFIX}/api/handshake', methods=["GET", "OPTIONS"])
def API_Handshake():
    return ResponseObject(True)
```

```python
@app.get(f'{APP_PREFIX}/api/isTotpEnabled')
def API_isTotpEnabled():
    return (
        ResponseObject(data=DashboardConfig.GetConfig("Account", "enable_totp")[1] and DashboardConfig.GetConfig("Account", "totp_verified")[1]))
```

```python
@app.get(f'{APP_PREFIX}/api/getDashboardConfiguration')
def API_getDashboardConfiguration():
    cfg = DashboardConfig.toJson()
    _, port = DashboardConfig.GetConfig("Peers", "remote_endpoint_port")
    cfg["Peers"]["remote_endpoint_port"] = port
    return ResponseObject(data=cfg)
```

These endpoints let the app confirm the server is reachable, check if OTP is required, and determine if API keys are enabled.

## Project Setup

1. **Create a new project** in Xcode using the **App** template. Choose
   **SwiftUI** for the interface and **Swift** for the language.
2. Pick an appropriate **Product Name** (e.g. `WGDashboardClient`) and save
   the project to a convenient location.
3. In the Project Navigator you will see two files generated for you:
   `YourAppNameApp.swift` and `ContentView.swift`. These will be modified in the
   steps below.
4. For each Swift file mentioned later (`SessionManager.swift`,
   `NetworkManager.swift`, `ServerSetupView.swift`, `DashboardView.swift`), add a
   new file via **File → New → File…** and choose the **Swift File** template.

Once the files are in place you can copy the code snippets below into their
respective files.

### File overview

Create the following Swift source files in your Xcode project. Use **File → New → File…** and select the **Swift File** template for each name.  The purpose of every file is listed so you know where each block of code belongs.

| File name | Purpose |
|-----------|---------|
| `SessionManager.swift` | Stores the server URL, API key and authentication state. |
| `NetworkManager.swift` | Handles all WGDashboard API calls. |
| `ServerSetupView.swift` | Prompts for the dashboard URL and optional API key. |
| `ContentView.swift` | Login form with username, password and OTP fields. |
| `DashboardView.swift` | Displays WireGuard configuration lists and system status. |
| `ConfigurationDetailView.swift` | Shows peers and traffic for a single configuration. |

Paste the matching code from each section below into the corresponding file.

## 1. SessionManager
Create or update `SessionManager.swift`:

```swift
import Foundation

class SessionManager: ObservableObject {
    @Published var isAuthenticated = false
    @Published var serverURL: URL? {
        didSet { UserDefaults.standard.set(serverURL?.absoluteString, forKey: "serverURL") }
    }
    @Published var apiKey: String? {
        didSet { UserDefaults.standard.set(apiKey, forKey: "apiKey") }
    }

    init() {
        if let str = UserDefaults.standard.string(forKey: "serverURL") {
            serverURL = URL(string: str)
        }
        apiKey = UserDefaults.standard.string(forKey: "apiKey")
    }
}
```

## 2. NetworkManager
Replace the static `baseURL` with a property that can be set at runtime. Add functions to fetch the dashboard configuration and OTP status.

```swift
import Foundation

final class NetworkManager {
    static let shared = NetworkManager()

    private var baseURL: URL?
    private var session: URLSession
    private init() {
        let config = URLSessionConfiguration.default
        config.httpCookieStorage = .shared
        session = URLSession(configuration: config)
    }

    func configure(baseURL: URL, apiKey: String?) {
        self.baseURL = baseURL
        if let key = apiKey {
            session.configuration.httpAdditionalHeaders = ["wg-dashboard-apikey": key]
        } else {
            session.configuration.httpAdditionalHeaders = nil
        }
    }

    func handshake(completion: @escaping (Bool) -> Void) {
        guard let url = baseURL?.appendingPathComponent("api/handshake") else { completion(false); return }
        session.dataTask(with: url) { data, _, _ in
            completion(data != nil)
        }.resume()
    }

    func fetchDashboardConfig(completion: @escaping ([String: Any]?) -> Void) {
        guard let url = baseURL?.appendingPathComponent("api/getDashboardConfiguration") else { completion(nil); return }
        session.dataTask(with: url) { data, _, _ in
            guard
                let data = data,
                let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                let dataDict = obj["data"] as? [String: Any]
            else { completion(nil); return }
            completion(dataDict)
        }.resume()
    }

    func isTotpEnabled(completion: @escaping (Bool) -> Void) {
        guard let url = baseURL?.appendingPathComponent("api/isTotpEnabled") else { completion(false); return }
        session.dataTask(with: url) { data, _, _ in
            guard
                let data = data,
                let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                let enabled = obj["data"] as? Bool
            else { completion(false); return }
            completion(enabled)
        }.resume()
    }

    func authenticate(username: String, password: String, totp: String?,
                      completion: @escaping (Bool, String?) -> Void) {
        guard let url = baseURL?.appendingPathComponent("api/authenticate") else {
            completion(false, "Bad URL"); return
        }
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let body: [String: String] = [
            "username": username,
            "password": password,
            "totp": totp ?? ""
        ]
        request.httpBody = try? JSONEncoder().encode(body)

        session.dataTask(with: request) { data, _, _ in
            guard
                let data = data,
                let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                let status = obj["status"] as? Bool
            else { completion(false, "Network error"); return }
            completion(status, obj["message"] as? String)
        }.resume()
    }

    func fetchConfigurations(completion: @escaping ([Configuration]?) -> Void) {
        guard let url = baseURL?.appendingPathComponent("api/getWireguardConfigurations") else { completion(nil); return }
        session.dataTask(with: url) { data, _, _ in
            guard
                let data = data,
                let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                let status = obj["status"] as? Bool,
                status,
                let arr = obj["data"] as? [[String: Any]]
            else { completion(nil); return }

            if let json = try? JSONSerialization.data(withJSONObject: arr),
               let configs = try? JSONDecoder().decode([Configuration].self, from: json) {
                completion(configs)
            } else {
                completion(nil)
            }
        }.resume()
    }
}
```

## 3. ServerSetupView
Add a SwiftUI view that prompts for the server URL and (if required) an API key. Users may enter a full URL such as `https://example.com/prefix` or just a host/IP with a port like `192.168.2.43:10086`. If the input lacks a scheme, the view assumes `http://` automatically. Validate the address with `handshake` and `getDashboardConfiguration`.

```swift
import SwiftUI

struct ServerSetupView: View {
    @EnvironmentObject var session: SessionManager
    @State private var urlString = ""
    @State private var apiKey = ""
    @State private var requireApiKey = false
    @State private var error: String?

    var body: some View {
        Form {
            Section("Server") {
                TextField("https://example.com/prefix", text: $urlString)
                    .keyboardType(.URL)
                    .textInputAutocapitalization(.never)
            }
            if requireApiKey {
                Section("API Key") {
                    SecureField("API Key", text: $apiKey)
                }
            }
            if let err = error {
                Text(err).foregroundColor(.red)
            }
            Button("Continue", action: validate)
        }
        .navigationTitle("Connect")
    }

    private func makeURL(from text: String) -> URL? {
        if let url = URL(string: text), url.scheme != nil {
            return url
        }
        return URL(string: "http://\(text)")
    }

    private func validate() {
        guard let url = makeURL(from: urlString) else { error = "Invalid URL"; return }
        NetworkManager.shared.configure(baseURL: url, apiKey: nil)
        NetworkManager.shared.handshake { ok in
            guard ok else { DispatchQueue.main.async { self.error = "Server unreachable" }; return }
            NetworkManager.shared.fetchDashboardConfig { cfg in
                DispatchQueue.main.async {
                    guard let cfg = cfg else { self.error = "Config failed"; return }
                    if let server = cfg["Server"] as? [String: Any],
                       let apiKeyOn = server["dashboard_api_key"] as? String,
                       apiKeyOn == "true", !self.requireApiKey {
                        self.requireApiKey = true
                        self.error = "API key required"
                    } else {
                        NetworkManager.shared.configure(baseURL: url, apiKey: self.requireApiKey ? self.apiKey : nil)
                        session.serverURL = url
                        session.apiKey = self.requireApiKey ? self.apiKey : nil
                        session.isAuthenticated = false
                    }
                }
            }
        }
    }
}
```

## 4. ContentView.swift
Before showing the login form, check whether OTP is enabled by calling `isTotpEnabled`. This snippet includes the full sign‑in logic and `isSigningIn` flag so the button shows a progress view while the request is running.

```swift
struct ContentView: View {
    @EnvironmentObject var session: SessionManager
    @State private var username = ""
    @State private var password = ""
    @State private var otp = ""
    @State private var otpRequired = false
    @State private var isSigningIn = false
    @State private var errorText: String?

    var body: some View {
        NavigationStack {
            VStack(spacing: 16) {
                TextField("Username", text: $username)
                    .textFieldStyle(.roundedBorder)
                SecureField("Password", text: $password)
                    .textFieldStyle(.roundedBorder)
                if otpRequired {
                    TextField("OTP from your authenticator", text: $otp)
                        .textFieldStyle(.roundedBorder)
                        .keyboardType(.numberPad)
                }
                if let err = errorText {
                    Text(err).foregroundColor(.red)
                }
                Button(action: signIn) {
                    if isSigningIn {
                        ProgressView("Signing In…")
                    } else {
                        Label("Sign In", systemImage: "chevron.right")
                    }
                }
                .buttonStyle(.borderedProminent)
                .disabled(isSigningIn || username.isEmpty || password.isEmpty)
            }
            .padding()
            .navigationTitle("WGDashboard")
            .toolbar {
                Button("Change Server") {
                    session.serverURL = nil
                }
            }
            .onAppear { NetworkManager.shared.isTotpEnabled { self.otpRequired = $0 } }
        }
    }

    private func signIn() {
        isSigningIn = true
        NetworkManager.shared.authenticate(
            username: username,
            password: password,
            totp: otpRequired ? otp : nil
        ) { success, message in
            DispatchQueue.main.async {
                self.isSigningIn = false
                if success {
                    session.isAuthenticated = true
                } else {
                    self.errorText = message ?? "Authentication failed"
                }
            }
        }
    }
}
```

## 5. App Entry Point
Update `WGDashboardClientApp.swift` to show `ServerSetupView` if `serverURL` is not yet saved.

```swift
@main
struct WGDashboardClientApp: App {
    @StateObject private var session = SessionManager()

    var body: some Scene {
        WindowGroup {
            if session.serverURL == nil {
                NavigationStack { ServerSetupView() }.environmentObject(session)
            } else if session.isAuthenticated {
                DashboardView().environmentObject(session)
            } else {
                ContentView().environmentObject(session)
            }
        }
    }
}
```

With these additions, the app first prompts for the server URL (and API key if required). It stores the values using `UserDefaults` so the prompt only appears on first launch. A "Change Server" button on the login screen clears the stored URL so you can enter a new address. After validating the server, the login screen is shown and the OTP field only appears when `isTotpEnabled` returns `true`.

## Build and Run

1. Choose an iPhone simulator in the Xcode toolbar (for example **iPhone 15**).
2. Press **⌘R** or click the **Run** button to build the project.
3. When the app launches, enter the WGDashboard server URL. Provide the API key if the setup view indicates one is required.
4. After the server is validated the login form appears. Signing in will show the list of WireGuard configurations retrieved from your dashboard.

## Displaying Dashboard Data

Once authentication succeeds you can fetch the same statistics shown in the web
dashboard.  Two additional endpoints provide this data.

### 1. System Status

`GET /api/systemStatus` returns CPU, memory and disk usage information. Extend
`NetworkManager` with a helper for this request and create a structure to hold
the response:

```swift
struct SystemStatus: Decodable {
    struct CPU: Decodable { let cpu_percent: Double; let cpu_percent_per_cpu: [Double] }
    struct MemInfo: Decodable { let percent: Double }
    struct Memory: Decodable { let VirtualMemory: MemInfo; let SwapMemory: MemInfo }
    struct Disk: Decodable { let mountPoint: String; let percent: Double }

    let CPU: CPU
    let Memory: Memory
    let Disks: [Disk]
}

extension NetworkManager {
    func fetchSystemStatus(completion: @escaping (SystemStatus?) -> Void) {
        guard let url = baseURL?.appendingPathComponent("api/systemStatus") else { completion(nil); return }
        session.dataTask(with: url) { data, _, _ in
            guard
                let data = data,
                let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                let json = obj["data"],
                let jsonData = try? JSONSerialization.data(withJSONObject: json),
                let status = try? JSONDecoder().decode(SystemStatus.self, from: jsonData)
            else { completion(nil); return }
            completion(status)
        }.resume()
    }
}
```

### 2. Configuration Detail

To display address, port, public key and peer statistics for a specific
configuration, call
`GET /api/getWireguardConfigurationInfo?configurationName=NAME`.

```swift
struct ConfigurationInfo: Decodable {
    let Name: String
    let Address: String
    let ListenPort: Int
    let PublicKey: String
    let Status: Bool
}

struct Peer: Identifiable, Decodable {
    let id: String
    let name: String
    let allowed_ip: String
    let total_sent: Double
    let total_receive: Double
    let status: String
}

struct ConfigurationDetail: Decodable {
    let configurationInfo: ConfigurationInfo
    let configurationPeers: [Peer]
    let configurationRestrictedPeers: [Peer]
}

extension NetworkManager {
    func fetchConfigurationInfo(name: String, completion: @escaping (ConfigurationDetail?) -> Void) {
        guard let base = baseURL else { completion(nil); return }
        var comps = URLComponents(url: base.appendingPathComponent("api/getWireguardConfigurationInfo"), resolvingAgainstBaseURL: false)
        comps?.queryItems = [URLQueryItem(name: "configurationName", value: name)]
        guard let url = comps?.url else { completion(nil); return }
        session.dataTask(with: url) { data, _, _ in
            guard
                let data = data,
                let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                let json = obj["data"],
                let jsonData = try? JSONSerialization.data(withJSONObject: json),
                let detail = try? JSONDecoder().decode(ConfigurationDetail.self, from: jsonData)
            else { completion(nil); return }
            completion(detail)
        }.resume()
    }
}
```

### 3. DashboardView Example

Combine these calls to present a basic dashboard after login:

```swift
struct DashboardView: View {
    @State private var system: SystemStatus?
    @State private var configs: [Configuration] = []

    var body: some View {
        NavigationStack {
            List {
                if let s = system {
                    Section("System Status") {
                        Text("CPU: \(s.CPU.cpu_percent, specifier: "%.1f")%")
                        Text("RAM: \(s.Memory.VirtualMemory.percent, specifier: "%.1f")%")
                    }
                }
                Section("WireGuard Configurations") {
                    ForEach(configs) { cfg in
                        NavigationLink(cfg.ConfigurationName) {
                            ConfigurationDetailView(name: cfg.ConfigurationName)
                        }
                    }
                }
            }
            .navigationTitle("Dashboard")
            .task { load() }
        }
    }

    private func load() {
        NetworkManager.shared.fetchSystemStatus { self.system = $0 }
        NetworkManager.shared.fetchConfigurations { self.configs = $0 ?? [] }
    }
}
```

### 4. ConfigurationDetailView Example

Create a new file named `ConfigurationDetailView.swift`. Make sure to import
`SwiftUI` so the `View` protocol and the `@State` property wrapper are
available.  This view fetches the details for a single configuration and shows
its peers and interface information.

```swift
import SwiftUI

struct ConfigurationDetailView: View {
    let name: String
    @State private var detail: ConfigurationDetail?

    var body: some View {
        List {
            if let info = detail?.configurationInfo {
                Section("Interface") {
                    Text("Address: \(info.Address)")
                    Text("Listen Port: \(info.ListenPort)")
                    Text("Public Key: \(info.PublicKey)")
                }
            }
            if let peers = detail?.configurationPeers {
                Section("Peers") {
                    ForEach(peers) { peer in
                        VStack(alignment: .leading) {
                            Text(peer.name)
                            Text(peer.allowed_ip).font(.caption)
                        }
                    }
                }
            }
        }
        .navigationTitle(name)
        .task { load() }
    }

    private func load() {
        NetworkManager.shared.fetchConfigurationInfo(name: name) { info in
            DispatchQueue.main.async { self.detail = info }
        }
    }
}
```

With this separate view in its own file, `DashboardView` no longer conflicts
with `ConfigurationDetailView`, and the app compiles without the redeclaration
errors.

## Next Steps

Use the remaining API endpoints in `dashboard.py` (for toggling a
configuration, running diagnostics, etc.) to continue mirroring features from
the browser dashboard.

## Additional API Reference

The following endpoints expose the rest of the data visible in the browser dashboard. Each call returns a JSON object with at least `status` and `message` fields.

| Endpoint | Purpose |
| --- | --- |
| `/api/getWireguardConfigurationRealtimeTraffic` | live peer traffic for a configuration |
| `/api/getWireguardConfigurationBackup` | list backups for a configuration |
| `/api/getAllWireguardConfigurationBackup` | list backups for every configuration |
| `/api/toggleWireguardConfiguration` | enable or disable a configuration |
| `/api/updateWireguardConfiguration` | update a configuration using a JSON payload |
| `/api/updateWireguardConfigurationRawFile` | upload the raw configuration file |
| `/api/deleteWireguardConfiguration` | delete a configuration |
| `/api/renameWireguardConfiguration` | rename a configuration |
| `/api/ping/execute` | run a ping from the server |
| `/api/traceroute/execute` | run traceroute from the server |
| `/api/getDashboardUpdate` | check for updates |
| `/api/getDashboardVersion` | retrieve the dashboard version |
| `/api/getDashboardTheme` | current theme settings |

### Example: Toggle a Configuration

```swift
extension NetworkManager {
    func toggleConfiguration(name: String, completion: @escaping (Bool) -> Void) {
        guard let base = baseURL else { completion(false); return }
        var comps = URLComponents(url: base.appendingPathComponent("api/toggleWireguardConfiguration"), resolvingAgainstBaseURL: false)
        comps?.queryItems = [URLQueryItem(name: "configurationName", value: name)]
        guard let url = comps?.url else { completion(false); return }
        session.dataTask(with: url) { data, _, _ in
            guard
                let data = data,
                let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                let status = obj["status"] as? Bool
            else { completion(false); return }
            completion(status)
        }.resume()
    }
}
```

### Example: Ping and Traceroute

```swift
extension NetworkManager {
    func ping(address: String, completion: @escaping (String?) -> Void) {
        guard let base = baseURL else { completion(nil); return }
        var comps = URLComponents(url: base.appendingPathComponent("api/ping/execute"), resolvingAgainstBaseURL: false)
        comps?.queryItems = [URLQueryItem(name: "ipAddress", value: address)]
        guard let url = comps?.url else { completion(nil); return }
        session.dataTask(with: url) { data, _, _ in
            guard
                let data = data,
                let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                let result = obj["data"] as? String
            else { completion(nil); return }
            completion(result)
        }.resume()
    }

    func traceroute(address: String, completion: @escaping (String?) -> Void) {
        guard let base = baseURL else { completion(nil); return }
        var comps = URLComponents(url: base.appendingPathComponent("api/traceroute/execute"), resolvingAgainstBaseURL: false)
        comps?.queryItems = [URLQueryItem(name: "ipAddress", value: address)]
        guard let url = comps?.url else { completion(nil); return }
        session.dataTask(with: url) { data, _, _ in
            guard
                let data = data,
                let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                let result = obj["data"] as? String
            else { completion(nil); return }
            completion(result)
        }.resume()
    }
}
```

These additional calls allow your prototype to mirror most sections of the WGDashboard web interface. The next sections show how to access the remaining features so your app can match everything the browser dashboard offers.

## Backups and Advanced Operations

The dashboard exposes several routes for creating and managing configuration backups. Add the following helpers in `NetworkManager`.

### Listing Backups

```swift
extension NetworkManager {
    func fetchBackups(for name: String, completion: @escaping ([String]?) -> Void) {
        guard let base = baseURL else { completion(nil); return }
        var comps = URLComponents(url: base.appendingPathComponent("api/getWireguardConfigurationBackup"), resolvingAgainstBaseURL: false)
        comps?.queryItems = [URLQueryItem(name: "configurationName", value: name)]
        guard let url = comps?.url else { completion(nil); return }
        session.dataTask(with: url) { data, _, _ in
            guard
                let data = data,
                let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                let files = obj["data"] as? [String]
            else { completion(nil); return }
            completion(files)
        }.resume()
    }

    func fetchAllBackups(completion: @escaping ([String: Any]?) -> Void) {
        guard let url = baseURL?.appendingPathComponent("api/getAllWireguardConfigurationBackup") else { completion(nil); return }
        session.dataTask(with: url) { data, _, _ in
            guard
                let data = data,
                let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                let result = obj["data"] as? [String: Any]
            else { completion(nil); return }
            completion(result)
        }.resume()
    }
}
```

### Creating, Restoring and Deleting Backups

```swift
extension NetworkManager {
    func createBackup(name: String, completion: @escaping (Bool) -> Void) {
        guard let base = baseURL else { completion(false); return }
        var comps = URLComponents(url: base.appendingPathComponent("api/createWireguardConfigurationBackup"), resolvingAgainstBaseURL: false)
        comps?.queryItems = [URLQueryItem(name: "configurationName", value: name)]
        guard let url = comps?.url else { completion(false); return }
        session.dataTask(with: url) { data, _, _ in
            guard
                let data = data,
                let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                let status = obj["status"] as? Bool
            else { completion(false); return }
            completion(status)
        }.resume()
    }

    func restoreBackup(name: String, file: String, completion: @escaping (Bool) -> Void) {
        guard let url = baseURL?.appendingPathComponent("api/restoreWireguardConfigurationBackup") else { completion(false); return }
        var req = URLRequest(url: url)
        req.httpMethod = "POST"
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.httpBody = try? JSONEncoder().encode(["ConfigurationName": name, "BackupFileName": file])
        session.dataTask(with: req) { data, _, _ in
            guard
                let data = data,
                let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                let status = obj["status"] as? Bool
            else { completion(false); return }
            completion(status)
        }.resume()
    }

    func deleteBackup(name: String, file: String, completion: @escaping (Bool) -> Void) {
        guard let url = baseURL?.appendingPathComponent("api/deleteWireguardConfigurationBackup") else { completion(false); return }
        var req = URLRequest(url: url)
        req.httpMethod = "POST"
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.httpBody = try? JSONEncoder().encode(["ConfigurationName": name, "BackupFileName": file])
        session.dataTask(with: req) { data, _, _ in
            guard
                let data = data,
                let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                let status = obj["status"] as? Bool
            else { completion(false); return }
            completion(status)
        }.resume()
    }
}
```

### Updating and Deleting Configurations

```swift
extension NetworkManager {
    func renameConfiguration(_ old: String, to new: String, completion: @escaping (Bool) -> Void) {
        guard let url = baseURL?.appendingPathComponent("api/renameWireguardConfiguration") else { completion(false); return }
        var req = URLRequest(url: url)
        req.httpMethod = "POST"
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.httpBody = try? JSONEncoder().encode(["ConfigurationName": old, "NewConfigurationName": new])
        session.dataTask(with: req) { data, _, _ in
            guard
                let data = data,
                let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                let status = obj["status"] as? Bool
            else { completion(false); return }
            completion(status)
        }.resume()
    }

    func deleteConfiguration(_ name: String, completion: @escaping (Bool) -> Void) {
        guard let base = baseURL else { completion(false); return }
        var comps = URLComponents(url: base.appendingPathComponent("api/deleteWireguardConfiguration"), resolvingAgainstBaseURL: false)
        comps?.queryItems = [URLQueryItem(name: "configurationName", value: name)]
        guard let url = comps?.url else { completion(false); return }
        session.dataTask(with: url) { data, _, _ in
            guard
                let data = data,
                let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                let status = obj["status"] as? Bool
            else { completion(false); return }
            completion(status)
        }.resume()
    }
}
```

### Dashboard Version and Updates

```swift
extension NetworkManager {
    func checkForUpdate(completion: @escaping (Bool) -> Void) {
        guard let url = baseURL?.appendingPathComponent("api/getDashboardUpdate") else { completion(false); return }
        session.dataTask(with: url) { data, _, _ in
            guard
                let data = data,
                let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                let status = obj["data"] as? Bool
            else { completion(false); return }
            completion(status)
        }.resume()
    }

    func fetchDashboardVersion(completion: @escaping (String?) -> Void) {
        guard let url = baseURL?.appendingPathComponent("api/getDashboardVersion") else { completion(nil); return }
        session.dataTask(with: url) { data, _, _ in
            guard
                let data = data,
                let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                let version = obj["data"] as? String
            else { completion(nil); return }
            completion(version)
        }.resume()
    }
}
```

With these helpers in place you can build views that list backups, rename or delete configurations, and display version details—everything available in the web dashboard.
