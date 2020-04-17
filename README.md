
# sanaserveri

A wordgame engine implemented in python.

## Description

The purpose of the game is to find words hidden in a table of random-looking characters. The server creates a 10x10 cell table with predefined words from three to ten letters and fills the rest of the table with random letters.

The server recognizes also words not hidden in the table delibrately but formed as the random arrangement of letters. Recognizing the words is done by checking against wordlists generated from the aspell dictionary of a chosen language.

Communication between the server and a client running the game fronnend is via JSON REST API.

## Installation

Before the server can run it needs the local wordlists. These are prepared by the provided makelists.sh script. The script requires aspell and relevant language dictionaries to be installed on the machine.
    
## Documentation

### User session handling

Each client must first register a session ID to access the API. The session ID is a sha1sum that is used as a key in all following API calls. This is the only call that does not require authentication.

```
client                                            server
------                                            ------
GET https://server:port/startsession   -->
     { }
                                           <--   { key: <RANDOM_SHA1SUM_40_CHARS>,
				                   status: "OK" }
```

### Getting wordlist

The client requests the table of characters prepared by the server. This operation needs the session key.

```
client                                            server
------                                            ------
GET https://server:port/getwords       -->
     { key: <RANDOM_SHA1SUM_40_CHARS> }
                                           <--   { table: [ ["O", "H", "J", "H", "C", "Y", "K", "G", "P", "B"],
					                    ["X", "B", "B", "Q", "X", "S", "N", "D", "V", "R"],
							    ["A", "S", "U", "M", "L", "U", "E", "L", "E", "I"],
							    ["C", "N", "A", "B", "A", "K", "E", "S", "D", "E"],
							    ["Q", "I", "H", "I", "C", "A", "J", "E", "L", "W"],
							    ["T", "O", "C", "X", "O", "L", "Z", "T", "U", "X"],
							    ["N", "J", "Y", "G", "M", "E", "R", "E", "F", "U"],
							    ["Q", "B", "S", "P", "D", "W", "I", "V", "L", "A"],
							    ["O", "U", "S", "Z", "W", "L", "S", "T", "L", "Y"],
							    ["T", "S", "H", "L", "G", "H", "A", "J", "Y", "C"] ],
				                   status: "OK" }
```

## License

Sanaserveri is available under the GPLv3 license.
