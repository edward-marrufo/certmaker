import os
import json


serverUrl = ""
serverconfigType = ""
serveroptionsPath = ""
serverconfigPath = ""
servercertPath = ""
serverkeyPath = ""


class Root:
    def __init__(self, configType, fullkeyPath, fulloptionsPath, fullconfigPath, fullcertPath):
        self.configType = configType
        self.fullkeyPath = fullkeyPath
        self.fulloptionsPath = fulloptionsPath
        self.fullconfigPath = fullconfigPath
        self.fullcertPath = fullcertPath

    def initCa(self):
        #checking if the rootca key exists
        if os.path.exists(self.fullkeyPath) == False:
            os.mkdir(self.configType)
            with open(self.fulloptionsPath) as configOptions:
                for line in configOptions:
                    with open(self.fulloptionsPath) as f:
                        data = f.read()
                        optionsDict = json.loads(data)
                        f.close()
            #saving bits and lifetime in days for later use
            for key, value in optionsDict.items():
                if "encryption_bits" in str(key):
                    encryptionBits = value

                if "life_time" in str(key):
                    lifeTime = value
            #creating the rootca key
            fullCommand = f"openssl genpkey -quiet -out {self.fullkeyPath} \
    -algorithm RSA \
    -pkeyopt rsa_keygen_bits:{encryptionBits}"
            os.system(fullCommand)

        
        #if our config doesn't exist, write a default one
        if os.path.exists(self.fullconfigPath) == False:
            default_config = """[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no

#required details about the issuer of the certificate
[req_distinguished_name]
countryName = Nothing
commonName = Nothing

[v3_req]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
basicConstraints = critical, CA:TRUE
keyUsage = nonRepudiation, keyCertSign, cRLSign

[crl_ext]
authorityKeyIdentifier = keyid:always,issuer"""

            f = open(self.fullconfigPath, "w")
            f.write(default_config)
            f.close()


        #writing the custom rootca config if we detect a default config
        if os.path.exists(self.fullconfigPath) == True:
            with open(self.fullconfigPath) as caConfig:
                for line in caConfig:
                    if "commonName = Nothing" in line:
                        try:
                            for key, value in optionsDict.items():
                                if "countryName" in str(key):
                                    countrynameOutput = f"sed -i 's/countryName = Nothing/countryName = {value}/' {self.fullconfigPath}"
                                    os.system(countrynameOutput)
                                elif "commonName" in str(key):
                                    commonnameOutput = f"sed -i 's/commonName = Nothing/commonName = {value}/' {self.fullconfigPath}"
                                    os.system(commonnameOutput)
                        except:
                            print("Creating root CA config failed")

        
        #generate our rootcert if a default config is not found and no cert is found
        if os.path.exists(self.fullconfigPath) == True and os.path.exists(self.fullcertPath) == False:
            with open(self.fullconfigPath) as caConfig:
                for line in caConfig:
                    if "commonName = Nothing" not in line:
                        try:
                            fullCommand = f"openssl req -config {self.fullconfigPath} -key {self.fullkeyPath} \
    -new -x509 -days {lifeTime} -sha256 -extensions v3_req -out {self.fullcertPath}"
                            os.system(fullCommand)
                        except:
                            print("Root cert generation failed")


class Server:
    def __init__(self, configType, fullkeyPath, fulloptionsPath, fullconfigPath, fullcertPath, siteName):
        self.configType = configType
        self.fullkeyPath = fullkeyPath
        self.fulloptionsPath = fulloptionsPath
        self.fullconfigPath = fullconfigPath
        self.fullcertPath = fullcertPath
        self.siteName = siteName

    def initServer(self):
        #checking if the rootca key exists
        if os.path.exists(self.fullkeyPath) == False:
            os.mkdir(self.siteName)
            with open(self.fulloptionsPath) as configOptions:
                for line in configOptions:
                    with open(self.fulloptionsPath) as f:
                        data = f.read()
                        optionsDict = json.loads(data)
                        f.close()
            #saving bits and lifetime in days for later use
            for key, value in optionsDict.items():
                if "encryption_bits" in str(key):
                    encryptionBits = value

                if "life_time" in str(key):
                    lifeTime = value
            #creating the rootca key
            fullCommand = f"openssl genpkey -quiet -out {self.fullkeyPath} \
    -algorithm RSA \
    -pkeyopt rsa_keygen_bits:{encryptionBits}"
            os.system(fullCommand)

        #creating the default config
        if os.path.exists(self.fullconfigPath) == False:
            default_config = """[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no

[req_distinguished_name]
countryName = Nothing
commonName = Nothing

[v3_req]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, keyEncipherment, digitalSignature
extendedKeyUsage = Nothing
subjectAltName = @alt_names

[alt_names]\n"""

        #writing out the default config
        f = open(self.fullconfigPath, "w")
        f.write(default_config)
        f.close()

        #modifying the default config if detected
        if os.path.exists(self.fullconfigPath) == True:
            with open(self.fullconfigPath) as serverConfig:
                for line in serverConfig:
                    if "commonName = Nothing" in line:
                        try:
                            for key, value in optionsDict.items():
                                if "DNS" in str(key):
                                    altnamesOutput = f"echo '{key} = {value}' >> {self.fullconfigPath}"
                                    os.system(altnamesOutput)
                                elif "IP" in str(key):
                                    altnamesOutput = f"echo '{key} = {value}' >> {self.fullconfigPath}"
                                    os.system(altnamesOutput)
                                elif "countryName" in str(key):
                                    countrynameOutput = f"sed -i 's/countryName = Nothing/countryName = {value}/' {self.fullconfigPath}"
                                    os.system(countrynameOutput)
                                elif "commonName" in str(key):
                                    commonnameOutput = f"sed -i 's/commonName = Nothing/commonName = {value}/' {self.fullconfigPath}"
                                    os.system(commonnameOutput)
                                elif "extendedKeyUsage" in str(key) and len(str(value)) > 0:
                                    extendedkeyusageOutput = f"sed -i 's/extendedKeyUsage = Nothing/extendedKeyUsage = {value}/' {self.fullconfigPath}"
                                    os.system(extendedkeyusageOutput)
                        except:
                            print("Modifying server config failed!")
            try:
                #writing out the CSR
                servPath = f"openssl req -new -config {self.fullconfigPath} -key {self.fullkeyPath} -out {self.siteName}/server.csr"
                os.system(servPath)
            except:
                print("Generating server CSR failed!")
            if os.path.exists("root/rootca.srl") == False:
                try:
                    #signing the csr and spitting out the cert
                    servPath = f"openssl x509 -req -in {self.siteName}/server.csr -CA rootca/rootca.crt -CAkey rootca/rootca.key \
    -CAcreateserial -out {self.siteName}/server.crt -days {lifeTime} -extensions v3_req \
    -extfile {self.fullconfigPath}"
                    os.system(servPath)
                except:
                    print("Generating server cert failed!")
            elif os.path.exists("root/rootca.srl") == True:
                try:
                    servPath = f"openssl x509 -req -in {self.siteName}/server.csr -CA rootca/rootca.crt -CAkey rootca/rootca.key \
    -CAserial root/rootca.srl -out {self.siteName}/server.crt -days {lifeTime} -extensions v3_req \
    -extfile {self.fullconfigPath}"
                    os.system(servPath)
                except:
                    print("Generating server cert failed!")

                
def readserverInfo():
    global serverUrl
    global serverconfigType
    global serveroptionsPath
    global serverconfigPath
    global servercertPath
    global serverkeyPath

    with open("servercert_options.yaml") as f:
        data = f.read()
        server_dict = json.loads(data)
        f.close()
    try:
        for key, value in server_dict.items():
            if "DNS.1" in str(key) and "www" in str(value):
                serverUrl = value
                serverconfigType = "server"
                serveroptionsPath = "servercert_options.yaml"
                serverconfigPath = f"{serverUrl}/server.conf"
                servercertPath = f"{serverUrl}/server.crt"
                serverkeyPath = f"{serverUrl}/server.key"
    except:
        print("Reading server config failed!")


def main():
    myRoot = Root("rootca", "rootca/rootca.key", "internalca_options.yaml", "rootca/rootca.conf", "rootca/rootca.crt")
    myRoot.initCa()
    readserverInfo()
    myServer = Server(serverconfigType, serverkeyPath, serveroptionsPath, serverconfigPath, servercertPath, serverUrl)
    myServer.initServer()

if __name__ == '__main__':
    main()
