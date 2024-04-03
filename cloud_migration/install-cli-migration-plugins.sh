#! /bin/bash

# JFrog hereby grants you a non-exclusive, non-transferable, non-distributable right to use this  code   solely in connection with your use of a JFrog product or service. This  code is provided 'as-is' and without any warranties or conditions, either express or implied including, without limitation, any warranties or conditions of title, non-infringement, merchantability or fitness for a particular cause. Nothing herein shall convey to you any right or title in the code, other than for the limited use right set forth herein. For the purposes hereof "you" shall mean you as an individual as well as the organization on behalf of which you are using the software and the JFrog product or service. 

## dyanamic inputs
SOURCE_RT_TOKEN="${1:?please provide the token for source JPD}" 
TARGET_RT_TOKEN="${2:?please provide the token for target JPD}" 

## script inputs
SaaS=true
SOURCE_JPD_URL="http://localhost:8082"
TARGET_JPD_URL="https://ramkannan.jfrog.io"
#DT_PLUGIN_VERSION="1.7.3"
#DT_PLUGIN_VERSION="[RELEASE]"
CONFIG_IMPORT_PLUGIN_VERSION="1.3.1"
SAVE_DIR="/tmp/datatransfer/"
JFROG_HOME="/opt/jfrog"
# Set CLI home dir
export JFROG_CLI_HOME_DIR=/tmp/.jfrog

#cd /tmp/ ; mkdir -p $SAVE_DIR
mkdir -p $SAVE_DIR ; cd $SAVE_DIR

echo -e "\nDownloading DATA TRANSFER Plugins.."
#curl -k -O -g  "$SAVE_DIR/dataTransfer.groovy" "https://releases.jfrog.io/artifactory/jfrog-releases/data-transfer/$DT_PLUGIN_VERSION/dataTransfer.groovy" -s
#curl -k -O -g  "$SAVE_DIR/data-transfer.jar" "https://releases.jfrog.io/artifactory/jfrog-releases/data-transfer/$DT_PLUGIN_VERSION/lib/data-transfer.jar" -s
curl -k -O -g  https://releases.jfrog.io/artifactory/jfrog-releases/data-transfer/\[RELEASE\]/dataTransfer.groovy
curl -k -O -g  https://releases.jfrog.io/artifactory/jfrog-releases/data-transfer/\[RELEASE\]/lib/data-transfer.jar
chown artifactory:artifactory "$SAVE_DIR/dataTransfer.groovy"
chown artifactory:artifactory "$SAVE_DIR/data-transfer.jar"
echo -e "\nPlugins Download DATA TRANSFER Completed..."

if [ "$SaaS" = false ] ; then
    echo "its OnPrem to OnPrem Transfer"
    echo -e "\nDownloading CONFIG IMPORT Plugins.."
    curl -k -O -g  "$SAVE_DIR/configImport.groovy" "https://releases.jfrog.io/artifactory/jfrog-releases/config-import/$CONFIG_IMPORT_PLUGIN_VERSION/configImport.groovy" -s
    curl -k -O -g  "$SAVE_DIR/config-import.jar" "https://releases.jfrog.io/artifactory/jfrog-releases/config-import/$CONFIG_IMPORT_PLUGIN_VERSION/lib/config-import.jar" -s
    chown artifactory:artifactory "$SAVE_DIR/configImport.groovy"
    chown artifactory:artifactory "$SAVE_DIR/config-import.jar"
    echo -e "\nPlugins CONFIG IMPORT Download Completed..."
fi

echo -e "\nInstalling/Downloading JFrog CLI.."
# use in case of docker cli
# cd /tmp/ ; curl -fkL https://getcli.jfrog.io/v2-jf | sh ; chmod +x jf ; export JFROG_CLI_HOME_DIR=/tmp/.jfrog

curl -fkL https://install-cli.jfrog.io  | sh

jf c add source-server --url="${SOURCE_JPD_URL}" --access-token="${SOURCE_RT_TOKEN}" --interactive=false

jf rt ping

export JFROG_HOME="$JFROG_HOME"

jf rt transfer-plugin-install source-server --dir "$SAVE_DIR"

jf c add target-server --url="${TARGET_JPD_URL}" --access-token="${TARGET_RT_TOKEN}" --interactive=false

jf rt ping --server-id=target-server

if [ "$SaaS" = false ] ; then
    echo "its OnPrem to OnPrem Transfer"
    cp -f "$SAVE_DIR/configImport.groovy" /opt/jfrog/artifactory/var/etc/artifactory/plugins/configImport.groovy
    cp -f "$SAVE_DIR/config-import.jar" /opt/jfrog/artifactory/var/etc/artifactory/plugins/lib/config-import.jar
    jf rt curl -X POST /api/plugins/reload 
fi

### sample cmd to run - ./install-cli-migration-plugins.sh **** ****