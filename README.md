# Certmaker

The idea behind this tool came to be due the difficulty in remembering all of the commands needed to create a basic working TLS setup. During basic development or testing purposes this slows down the entire process. Thus Certmaker was born. Under the hood, it is nothing more than native openssl commands.

### How it works
After cloning the repository first you need to modify the servercert_options.yaml to include the FQDN of the service that needs to be secured. For example:

```
{
  "DNS.1": "www.example.com",
  "DNS.2": "example.com",
  "commonName": "www.example.com",
  "countryName": "US",
  "life_time": "398",
  "extendedKeyUsage": "serverAuth",
  "encryption_bits": "2048"
}
```
<br>
<br>
The only thing you will need to change by default is the DNS.1, DNS.2, and commonName settings. Say for example you wanted to host a new service at service.example.com. Your new file would then look like:
<br>
<br>

```
{
  "DNS.1": "www.service.example.com",
  "DNS.2": "service.example.com",
  "commonName": "www.service.example.com",
  "countryName": "US",
  "life_time": "398",
  "extendedKeyUsage": "serverAuth",
  "encryption_bits": "2048"
}
```
<br>
<br>
Once you save your new file then do a simple:
<br>
<br>

```
docker compose build
docker compose up -d
```
<br>
<br>

You should have two directories created, *rootca* and also *www.service.example.com*. The only thing you will need to do at this point is transfer rootca.crt (located inside rootca directory), server.crt, and server.key (both located in www.service.example.com directory) to whatever server is hosting your service. If you need to create another cert then you only need to first:

<br>
<br>

```
docker compose down
```

Modify your server file again and then bring it up once more. You won't lose the previous cert or key nor the root ca as another new directory will be created. If you need to add IP addresses you only need to modify the servercert_options.yaml to include something like below:


```
{
  "DNS.1": "www.someotherservice.example.com",
  "DNS.2": "someotherservice.example.com",
  "IP.1": "192.168.1.1",
  "IP.2": "192.168.1.2",
  "commonName": "www.someotherservice.example.com",
  "countryName": "US",
  "life_time": "398",
  "extendedKeyUsage": "serverAuth",
  "encryption_bits": "2048"
}
```
<br>
<br>


### Known limitations
- In order for things to work correctly, DNS.1 must match www.example.com scheme and start with www.
- Since the container image is not hosted in any container registries you will need to build this for the first time, however you only need to do this once.
- Currently only pkcs8 RSA keys and the documented options are supported.
- This is **NOT** meant to be used on production servers, only for testing/development purposes.