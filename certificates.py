from OpenSSL import crypto, SSL

# Generate a key
key = crypto.PKey()
key.generate_key(crypto.TYPE_RSA, 2048)

# Create a self-signed cert
cert = crypto.X509()
cert.get_subject().C = "US"
cert.get_subject().ST = "California"
cert.get_subject().L = "San Francisco"
cert.get_subject().O = "My Company"
cert.get_subject().OU = "My Organization"
cert.get_subject().CN = "localhost"
cert.set_serial_number(1000)
cert.gmtime_adj_notBefore(0)
cert.gmtime_adj_notAfter(10*365*24*60*60)  # Ten years
cert.set_issuer(cert.get_subject())
cert.set_pubkey(key)
cert.sign(key, 'sha256')

with open("server.key", "wt") as f:
    f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key).decode("utf-8"))
with open("server.pem", "wt") as f:
    f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf-8"))
