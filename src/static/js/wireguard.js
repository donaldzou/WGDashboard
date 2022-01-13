/*! SPDX-License-Identifier: GPL-2.0
 *
 * Copyright (C) 2015-2020 Jason A. Donenfeld <Jason@zx2c4.com>. All Rights Reserved.
 */

(function() {
	function gf(init) {
		var r = new Float64Array(16);
		if (init) {
			for (var i = 0; i < init.length; ++i)
				r[i] = init[i];
		}
		return r;
	}

	function pack(o, n) {
		var b, m = gf(), t = gf();
		for (var i = 0; i < 16; ++i)
			t[i] = n[i];
		carry(t);
		carry(t);
		carry(t);
		for (var j = 0; j < 2; ++j) {
			m[0] = t[0] - 0xffed;
			for (var i = 1; i < 15; ++i) {
				m[i] = t[i] - 0xffff - ((m[i - 1] >> 16) & 1);
				m[i - 1] &= 0xffff;
			}
			m[15] = t[15] - 0x7fff - ((m[14] >> 16) & 1);
			b = (m[15] >> 16) & 1;
			m[14] &= 0xffff;
			cswap(t, m, 1 - b);
		}
		for (var i = 0; i < 16; ++i) {
			o[2 * i] = t[i] & 0xff;
			o[2 * i + 1] = t[i] >> 8;
		}
	}

	function carry(o) {
		var c;
		for (var i = 0; i < 16; ++i) {
			o[(i + 1) % 16] += (i < 15 ? 1 : 38) * Math.floor(o[i] / 65536);
			o[i] &= 0xffff;
		}
	}

	function cswap(p, q, b) {
		var t, c = ~(b - 1);
		for (var i = 0; i < 16; ++i) {
			t = c & (p[i] ^ q[i]);
			p[i] ^= t;
			q[i] ^= t;
		}
	}

	function add(o, a, b) {
		for (var i = 0; i < 16; ++i)
			o[i] = (a[i] + b[i]) | 0;
	}

	function subtract(o, a, b) {
		for (var i = 0; i < 16; ++i)
			o[i] = (a[i] - b[i]) | 0;
	}

	function multmod(o, a, b) {
		var t = new Float64Array(31);
		for (var i = 0; i < 16; ++i) {
			for (var j = 0; j < 16; ++j)
				t[i + j] += a[i] * b[j];
		}
		for (var i = 0; i < 15; ++i)
			t[i] += 38 * t[i + 16];
		for (var i = 0; i < 16; ++i)
			o[i] = t[i];
		carry(o);
		carry(o);
	}

	function invert(o, i) {
		var c = gf();
		for (var a = 0; a < 16; ++a)
			c[a] = i[a];
		for (var a = 253; a >= 0; --a) {
			multmod(c, c, c);
			if (a !== 2 && a !== 4)
				multmod(c, c, i);
		}
		for (var a = 0; a < 16; ++a)
			o[a] = c[a];
	}

	function clamp(z) {
		z[31] = (z[31] & 127) | 64;
		z[0] &= 248;
	}

	function generatePublicKey(privateKey) {
		var r, z = new Uint8Array(32);
		var a = gf([1]),
			b = gf([9]),
			c = gf(),
			d = gf([1]),
			e = gf(),
			f = gf(),
			_121665 = gf([0xdb41, 1]),
			_9 = gf([9]);
		for (var i = 0; i < 32; ++i)
			z[i] = privateKey[i];
		clamp(z);
		for (var i = 254; i >= 0; --i) {
			r = (z[i >>> 3] >>> (i & 7)) & 1;
			cswap(a, b, r);
			cswap(c, d, r);
			add(e, a, c);
			subtract(a, a, c);
			add(c, b, d);
			subtract(b, b, d);
			multmod(d, e, e);
			multmod(f, a, a);
			multmod(a, c, a);
			multmod(c, b, e);
			add(e, a, c);
			subtract(a, a, c);
			multmod(b, a, a);
			subtract(c, d, f);
			multmod(a, c, _121665);
			add(a, a, d);
			multmod(c, c, a);
			multmod(a, d, f);
			multmod(d, b, _9);
			multmod(b, e, e);
			cswap(a, b, r);
			cswap(c, d, r);
		}
		invert(c, c);
		multmod(a, a, c);
		pack(z, a);
		return z;
	}

	function generatePresharedKey() {
		var privateKey = new Uint8Array(32);
		window.crypto.getRandomValues(privateKey);
		return privateKey;
	}

	function generatePrivateKey() {
		var privateKey = generatePresharedKey();
		clamp(privateKey);
		return privateKey;
	}

	function encodeBase64(dest, src) {
		var input = Uint8Array.from([(src[0] >> 2) & 63, ((src[0] << 4) | (src[1] >> 4)) & 63, ((src[1] << 2) | (src[2] >> 6)) & 63, src[2] & 63]);
		for (var i = 0; i < 4; ++i)
			dest[i] = input[i] + 65 +
			(((25 - input[i]) >> 8) & 6) -
			(((51 - input[i]) >> 8) & 75) -
			(((61 - input[i]) >> 8) & 15) +
			(((62 - input[i]) >> 8) & 3);
	}

	function keyToBase64(key) {
		var i, base64 = new Uint8Array(44);
		for (i = 0; i < 32 / 3; ++i)
			encodeBase64(base64.subarray(i * 4), key.subarray(i * 3));
		encodeBase64(base64.subarray(i * 4), Uint8Array.from([key[i * 3 + 0], key[i * 3 + 1], 0]));
		base64[43] = 61;
		return String.fromCharCode.apply(null, base64);
	}

	function putU32(b, n)
	{
		b.push(n & 0xff, (n >>> 8) & 0xff, (n >>> 16) & 0xff, (n >>> 24) & 0xff);
	}

	function putU16(b, n)
	{
		b.push(n & 0xff, (n >>> 8) & 0xff);
	}

	function putBytes(b, a)
	{
		for (var i = 0; i < a.length; ++i)
			b.push(a[i] & 0xff);
	}

	function encodeString(s)
	{
		var utf8 = unescape(encodeURIComponent(s));
		var b = new Uint8Array(utf8.length);
		for (var i = 0; i < utf8.length; ++i)
			b[i] = utf8.charCodeAt(i);
		return b;
	}

	function crc32(b)
	{
		if (!crc32.table) {
			crc32.table = [];
			for (var c = 0, n = 0; n < 256; c = ++n) {
				for (var k = 0; k < 8; ++k)
					c = ((c & 1) ? (0xedb88320 ^ (c >>> 1)) : (c >>> 1));
				crc32.table[n] = c;
			}
		}
		var crc = -1;
		for (var i = 0; i < b.length; ++i)
			crc = (crc >>> 8) ^ crc32.table[(crc ^ b[i]) & 0xff];
		return (crc ^ (-1)) >>> 0;
	}

	function createZipFile(files)
	{
		var b = [];
		var cd = [];
		var offset = 0;

		for (var i = 0; i < files.length; ++i) {
			var name = encodeString(files[i].filename);
			var contents = encodeString(files[i].content);
			var crc = crc32(contents);

			putU32(b, 0x04034b50); /* signature */
			putU16(b, 20); /* version needed */
			putU16(b, 0); /* flags */
			putU16(b, 0); /* compression method */
			putU16(b, 0); /* mtime */
			putU16(b, 0); /* mdate */
			putU32(b, crc); /* crc32 */
			putU32(b, contents.length); /* compressed size */
			putU32(b, contents.length); /* uncompressed size */
			putU16(b, name.length); /* file name length */
			putU16(b, 0); /* extra field length */
			putBytes(b, name);
			putBytes(b, contents);

			putU32(cd, 0x02014b50); /* signature */
			putU16(cd, 0); /* version made */
			putU16(cd, 20); /* version needed */
			putU16(cd, 0); /* flags */
			putU16(cd, 0); /* compression method */
			putU16(cd, 0); /* mtime */
			putU16(cd, 0); /* mdate */
			putU32(cd, crc); /* crc32 */
			putU32(cd, contents.length); /* compressed size */
			putU32(cd, contents.length); /* uncompressed size */
			putU16(cd, name.length); /* file name length */
			putU16(cd, 0); /* extra field length */
			putU16(cd, 0); /* file comment length */
			putU16(cd, 0); /* disk number start */
			putU16(cd, 0); /* internal file attributes */
			putU32(cd, 32); /* external file attributes - 'archive' bit set (32) */
			putU32(cd, offset); /* relative offset of local header */
			putBytes(cd, name); /* file name */

			offset += 30 + contents.length + name.length
		}
		putBytes(b, cd); /* central directory */
		putU32(b, 0x06054b50); /* end of central directory signature */
		putU16(b, 0); /* number of this disk */
		putU16(b, 0); /* number of disk with central directory start */
		putU16(b, files.length); /* number of entries on disk */
		putU16(b, files.length); /* number of entries */
		putU32(b, cd.length); /* length of central directory */
		putU32(b, offset); /* offset to start of central directory */
		putU16(b, 0); /* zip comment size */
		return Uint8Array.from(b);
	}

	window.wireguard = {
		generateKeypair: function() {
			var privateKey = generatePrivateKey();
			var publicKey = generatePublicKey(privateKey);
			var presharedKey = generatePresharedKey();
			return {
				publicKey: keyToBase64(publicKey),
				privateKey: keyToBase64(privateKey),
				presharedKey: keyToBase64(presharedKey)
			};
		},
		generatePublicKey: function (privateKey){
			return keyToBase64(generatePublicKey(privateKey))
		},

		generateZipFiles: function(res){
			var files = res.peers;
			var zipFile = createZipFile(files);
			var blob = new Blob([zipFile], { type: "application/zip" });
			var a = document.createElement("a");
			a.download = res.filename;
			a.href = URL.createObjectURL(blob);
			a.style.display = "none";
			document.body.appendChild(a);
			a.click();
			document.body.removeChild(a);
		}
	};
})();
