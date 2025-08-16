import fs from 'fs'
import path from 'path'

function makePathsRelative() {
    const indexPath = path.join('dist', 'index.html')

    if (!fs.existsSync(indexPath)) {
        console.error('index.html not found in dist folder')
        return
    }

    let html = fs.readFileSync(indexPath, 'utf8')

    // Handle cases where Vite already added a base path
    html = html.replace(/(href|src)="\/static\/app\/dist\//g, '$1="./static/app/dist/')

    fs.writeFileSync(indexPath, html)
    console.log('✅ Converted all paths to ./static/app/dist/ in index.html')
}

makePathsRelative()