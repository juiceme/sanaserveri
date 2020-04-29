
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
     { "key": <RANDOM_SHA1SUM_40_CHARS> }
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

### Getting statistics

The client requests the statistics from the server. This operation needs the session key.

```
client                                            server
------                                            ------
GET https://server:port/getstatistics  -->
     { "key": <RANDOM_SHA1SUM_40_CHARS> }
                                           <--   { "statistics": { "score": 41,
								   "found_words": [ "YACHT",
								                    "LUNG" ],
								   "used_vectors": [ [ [0, 2], [1, 2], [2, 2], [3, 2], [4, 2] ],
								                     [ [9, 0], [8, 0], [7, 0], [6, 0] ] ] },
						  "status": "OK"}
```

### Getting current sessions

The client requests the current sessions on the server. This operation needs the session key and prior authorization as an administrator session.

```
client                                            server
------                                            ------
GET https://server:port/getsessions    -->
     { "key": <RANDOM_SHA1SUM_40_CHARS> }
                                           <--   { "sessions": [ { "key": "25723e53ac6c1f57550432c42e8e1487dbfdd95d",
					                           "score": 0,
								   "found_words": [],
								   "used_vectors": [] },
								 { "key": "2f7e3ec66b90eeca0fdb638cff3b7ab621bb361a",
								   "score": 41,
								   "found_words": [ "LUNG",
								                    "YACHT"],
								   "used_vectors": [ [ [9,0], [8,0], [7,0], [6,0] ],
								                     [ [0,2], [1,2], [2,2], [3,2], [4,2] ] ] },
						   "status": "OK"}


client                                            server
------                                            ------
GET https://server:port/getsessions    -->
     { "key": <RANDOM_SHA1SUM_40_CHARS> }
                                           <--   { "status": "FAIL",
					           "error": "No priviliges" }
```

### Sending a word to be checked

The client sends the vector of coordinates to the server. This operation needs the session key. The server checks the vector for validity and content, and if a valid word is found from vocabulary the statistics of the session are updated.

```
client                                            server
------                                            ------
PUT https://server:port/checkword      -->
     { "word": "[[8,9],[8,8],[8,7],[8,6],[8,5],[8,4],[8,3]]"
     "key": <RANDOM_SHA1SUM_40_CHARS> }
                                           <--   { "status": "FAIL",
					           "error": "Not a word" }


client                                            server
------                                            ------
PUT https://server:port/checkword      -->
     { "word": "[[6,7],[6,6],[6,5],[7,5],[7,4]]"
       "key": <RANDOM_SHA1SUM_40_CHARS> }
                                           <--   { "word": "IONIC",
					           "score": 25,
						   "status": "OK" }


client                                            server
------                                            ------
PUT https://server:port/checkword      -->
     { "word": "[[6,7],[6,6],[6,5],[7,5],[7,4]]"
       "key": <RANDOM_SHA1SUM_40_CHARS> }
                                           <--   { "status": "FAIL",
					           "error": "Duplicate vector" }
```

### Logging in as a named user

The client sends an username and a hashed password to the server. This operation needs the session key. If the username is found, the password hash is checked and login granted. If username is not found, an new user is created and the password hash stored along with the username.

```
client                                            server
------                                            ------
PUT https://server:port/login          -->
     { "username": <username>
       "password": <SHA1SUM_40_CHARS>
       "key": <RANDOM_SHA1SUM_40_CHARS> }
                                           <--   { "status": "OK" }


client                                            server
------                                            ------
PUT https://server:port/login          -->
     { "username": <username>
       "password": <SHA1SUM_40_CHARS>
       "key": <RANDOM_SHA1SUM_40_CHARS> }
                                           <--   { "status": "FAIL",
					           "error": "Invalid password" }
```

## License

Sanaserveri is available under the GPLv3 license.
