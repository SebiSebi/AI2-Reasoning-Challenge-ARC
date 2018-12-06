#!/bin/bash

# For color printing, see https://en.wikipedia.org/wiki/ANSI_escape_code
CLEAR='\033[0m'
RED='\033[1;31m'
GREEN='\033[1;32m'
PURPLE='\033[1;35m'

if [ "$#" -ne 2 ];
then
	echo -e "${RED}Usage: ./exec.sh {Java class} {Heap limit}${CLEAR}"
	exit 1
fi

# The path to the java executable.
java_executable="${JAVA_HOME}/bin/java"

# The main class to run (package.MainClass).
main_class="$1"
heap_limit="$2"

mvn package
if [ "$?" -ne 0 ];
then
	echo ""
	echo -e "${RED}mvn package failed!${CLEAR}"
	exit 2
fi

mvn install
if [ "$?" -ne 0 ];
then
	echo ""
	echo -e "${RED}mvn install failed!${CLEAR}"
	exit 3
fi

echo ""
echo -e "${GREEN} Build succeeded. ${CLEAR}"
echo -e " Running: ${PURPLE}${main_class}${CLEAR} Heap size: ${heap_limit}"
echo ""

# The special string %classpath will be replaced by the project classpath as computed by Maven.
mvn exec:exec -Dexec.args="-Xmx${heap_limit} -classpath %classpath ${main_class}" -Dexec.executable=${java_executable}
