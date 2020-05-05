/*
 * compile with:
 * g++ -Wall -I/opt/curl/include -I/opt/libxml/include/libxml2 solverbot2.cpp -o solverbot2 -L/opt/curl/lib -L/opt/libxml/lib -lcurl
 *
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <string>
#include <curl/curl.h>
#include <iostream>
#include <fstream>
#include <vector>
#include <tuple>
#include <cstdlib>
#include "json.hpp"

using json = nlohmann::json;

class WebAccess {

public:
  WebAccess() {
    curl_global_init(CURL_GLOBAL_DEFAULT);
    conn = curl_easy_init();
    if(conn == NULL) {
      fprintf(stderr, "Failed to create CURL connection\n");
      exit(EXIT_FAILURE);
    }
  }
  ~WebAccess() {
    curl_easy_cleanup(conn);
  }
  int get(char* url, char* data);
  int put(char* url, char* data);
  std::string read(void) {
    return buffer;
  }

private:
  CURL *conn = NULL;
  char errorBuffer[CURL_ERROR_SIZE];
  std::string buffer;
  static int writer(char *data, size_t size, size_t nmemb, std::string *writerData) {
    if(writerData == NULL)
      return 0;
    writerData->append(data, size*nmemb);
    return size * nmemb;
  }

};

int WebAccess::get(char* url, char* data) {
  CURLcode code;
  struct curl_slist *headers=NULL;

  code = curl_easy_setopt(conn, CURLOPT_ERRORBUFFER, errorBuffer);
  if(code != CURLE_OK) {
    fprintf(stderr, "Failed to set error buffer [%d]\n", code);
    return false;
  }
  headers = curl_slist_append(headers, "Content-Type: application/json");
  code = curl_easy_setopt(conn, CURLOPT_HTTPHEADER, headers);
  if(code != CURLE_OK) {
    fprintf(stderr, "Failed to set http headers, [%d]\n", code);
    return false;
  }
  code = curl_easy_setopt(conn, CURLOPT_URL, url);
  if(code != CURLE_OK) {
    fprintf(stderr, "Failed to set URL [%s]\n", errorBuffer);
    return false;
  }
  code = curl_easy_setopt(conn, CURLOPT_CUSTOMREQUEST, "GET");
  if(code != CURLE_OK) {
    fprintf(stderr, "Failed to set curl to put request mode [%d]\n", code);
    return false;
  }
  code = curl_easy_setopt(conn, CURLOPT_POSTFIELDS, data);
  if(code != CURLE_OK) {
    fprintf(stderr, "Failed to set post data, [%d]\n", code);
    return false;
  }
  code = curl_easy_setopt(conn, CURLOPT_CAINFO, "./cert.pem");
  if(code != CURLE_OK) {
    fprintf(stderr, "Failed to trust selfsigned serts\n");
    return false;
  }
  code = curl_easy_setopt(conn, CURLOPT_SSL_VERIFYHOST, 0);
  if(code != CURLE_OK) {
    fprintf(stderr, "Failed to set verifyhost\n");
    return false;
  }
  code = curl_easy_setopt(conn, CURLOPT_FOLLOWLOCATION, 1L);
  if(code != CURLE_OK) {
    fprintf(stderr, "Failed to set redirect option [%s]\n", errorBuffer);
    return false;
  }
  
  code = curl_easy_setopt(conn, CURLOPT_WRITEFUNCTION, WebAccess::writer);
  if(code != CURLE_OK) {
    fprintf(stderr, "Failed to set writer [%s]\n", errorBuffer);
    return false;
  }
 
  code = curl_easy_setopt(conn, CURLOPT_WRITEDATA, &buffer);
  if(code != CURLE_OK) {
    fprintf(stderr, "Failed to set write data [%s]\n", errorBuffer);
    return false;
  }

  buffer = "";
  code = curl_easy_perform(conn);
  if(code != CURLE_OK) {
    fprintf(stderr, "Failed to start session, [%s]\n", errorBuffer);
    return false;
  }

  return true;
}

int WebAccess::put(char* url, char* data) {
  CURLcode code;
  struct curl_slist *headers=NULL;

  conn = curl_easy_init();
  if(conn == NULL) {
    fprintf(stderr, "Failed to create CURL connection\n");
    exit(EXIT_FAILURE);
  }
  code = curl_easy_setopt(conn, CURLOPT_ERRORBUFFER, errorBuffer);
  if(code != CURLE_OK) {
    fprintf(stderr, "Failed to set error buffer [%d]\n", code);
    return false;
  }
  headers = curl_slist_append(headers, "Content-Type: application/json");
  code = curl_easy_setopt(conn, CURLOPT_HTTPHEADER, headers);
  if(code != CURLE_OK) {
    fprintf(stderr, "Failed to set http headers, [%d]\n", code);
    return false;
  }
  code = curl_easy_setopt(conn, CURLOPT_URL, url);
  if(code != CURLE_OK) {
    fprintf(stderr, "Failed to set URL [%s]\n", errorBuffer);
    return false;
  }
  code = curl_easy_setopt(conn, CURLOPT_CUSTOMREQUEST, "PUT");
  if(code != CURLE_OK) {
    fprintf(stderr, "Failed to set curl to put request mode [%d]\n", code);
    return false;
  }
  code = curl_easy_setopt(conn, CURLOPT_POSTFIELDS, data);
  if(code != CURLE_OK) {
    fprintf(stderr, "Failed to set post data, [%d]\n", code);
    return false;
  }
  code = curl_easy_setopt(conn, CURLOPT_CAINFO, "./cert.pem");
  if(code != CURLE_OK) {
    fprintf(stderr, "Failed to trust selfsigned serts\n");
    return false;
  }
  code = curl_easy_setopt(conn, CURLOPT_SSL_VERIFYHOST, 0);
  if(code != CURLE_OK) {
    fprintf(stderr, "Failed to set verifyhost\n");
    return false;
  }
  code = curl_easy_setopt(conn, CURLOPT_FOLLOWLOCATION, 1L);
  if(code != CURLE_OK) {
    fprintf(stderr, "Failed to set redirect option [%s]\n", errorBuffer);
    return false;
  }
  
  code = curl_easy_setopt(conn, CURLOPT_WRITEFUNCTION, writer);
  if(code != CURLE_OK) {
    fprintf(stderr, "Failed to set writer [%s]\n", errorBuffer);
    return false;
  }
  
  code = curl_easy_setopt(conn, CURLOPT_WRITEDATA, &buffer);
  if(code != CURLE_OK) {
    fprintf(stderr, "Failed to set write data [%s]\n", errorBuffer);
    return false;
  }

  buffer = "";
  code = curl_easy_perform(conn);
  if(code != CURLE_OK) {
    fprintf(stderr, "Failed to start session, [%s]\n", errorBuffer);
    return false;
  }

  return true;
}


class WordList {
public:
  WordList() {
    std::ifstream fstream;
    std::string filename, word;
    for(int i=3; i<11; i++) {
      filename = "words" + std::to_string(i);
      fstream.open(filename);
      if (!fstream) {
	fprintf(stderr, "Failed to open dictionary\n");
	exit(EXIT_FAILURE);
      }
      while (fstream >> word) {
	wordlist[i-3].push_back(word); 
      }
      fstream.close();
    }
  }

  ~WordList() {
  }

  bool is_word(std::string candidate) {
    if(candidate.length() < 3 || candidate.length() > 10) {
      return false;
    }
    for (auto & element : wordlist[candidate.length()-3]) {
      if(candidate.compare(element) == 0) {
	return true;
      }	
    }
    return false;
  }
  
private:
  std::vector<std::string> wordlist[8];
};


typedef std::vector< std::tuple<int, int> > wordvector;
typedef std::vector< wordvector > wordcollection;

class WordTable {
public:
  WordTable() {
    my_table = create_table();
  }

  ~WordTable() {
  }

  void set_table(char* table) {
    free(my_table);
    my_table = table;
  }

  std::string get_word(wordvector vw) {
    std::string word;
    for(const auto & element : vw) {
      int x = std::get<0>(element);
      int y = std::get<1>(element);
      int index = y+x*10;
      word.append(1, static_cast<char>(my_table[index]));
    }
    return word;
  }

  bool check_validity(wordvector vw) {
    wordvector copyvw = vw;
    wordvector::iterator it = std::unique( copyvw.begin(), copyvw.end() );
    if(it != copyvw.end()) {
      return false;
    }
    for(const auto & element : vw) {
      if(std::get<0>(element) < 0 || std::get<0>(element) > 9 ||
	 std::get<1>(element) < 0 || std::get<1>(element) > 9) {
	return false;
      }
    }
    int x0=10, y0=10, xdiff=0, ydiff=0;
    for(const auto & element : vw) {
      if(x0 != 10) {
	xdiff = std::abs(std::get<0>(element) - x0);
	ydiff = std::abs(std::get<1>(element) - y0);
	if(xdiff + ydiff != 1) {
	  return false;
	}
      }
      x0 = std::get<0>(element);
      y0 = std::get<1>(element);
    }
    return true;
  }

private:
  char* my_table;

  char* create_table(void) {
    char* table = (char*) malloc(sizeof(char[10][10]));
    for(int i=0; i<100; i++) {
      table[i] = '.';
    }
    return table;
  }
  
  char* duplicate_table(void) {
    char* table = create_table();
    for(int i=0; i<100; i++) {
      table[i] = my_table[i];
    }
    return table;
  }
    
};

wordcollection wc;

void solve(int i, int j, int depth, wordvector wv) {
  if(depth == 0) {
    wc.push_back(wv);
    return;
  } else {
    wv.push_back(std::make_tuple(i,j));
    wordvector wv1(wv);
    wordvector wv2(wv);
    wordvector wv3(wv);
    wordvector wv4(wv);
    solve(i, j-1, depth-1, wv1);
    solve(i, j+1, depth-1, wv2);
    solve(i-1, j, depth-1, wv3);
    solve(i+1, j, depth-1, wv4);
  }
}

int main(int argc, char *argv[])
{
  WordList wl;
  WordTable wt;
  WebAccess access;
  std::string url, data;
  json jii;

  //  std::cout << wl.is_word("KAZOOS")  << "\n";
    
  url = "https://localhost:8088/startsession";
  if(access.get((char *)(url.c_str()), (char *)"") == false) {
    fprintf(stderr, "Connection failed\n");
    exit(EXIT_FAILURE);
  }
  jii = json::parse(access.read());
  if(jii["status"] != "OK") {
    fprintf(stderr, "Failed to get session key\n");
    exit(EXIT_FAILURE);
  }
  auto sessionkey = jii["key"].get<std::string>();
  std::cout << "Got session key: " << sessionkey << "\n";

  url = "https://localhost:8088/getwords";
  jii = {{"key", sessionkey}};
  data = jii.dump();
  if(access.get((char *)(url.c_str()), (char *)data.c_str()) == false) {
    fprintf(stderr, "Connection failed\n");
    exit(EXIT_FAILURE);
  }
  jii = json::parse(access.read());
  if(jii["status"] != "OK") {
    fprintf(stderr, "Failed to get wordtable\n");
    exit(EXIT_FAILURE);
  }
  auto wordtable =  jii["table"];
  std::cout << "Got wordtable: " << wordtable << "\n";

  char* newtable = (char*) malloc(sizeof(char[10][10])+1);
  for(int i=0; i<10; i++) {
    for(int j=0; j<10; j++) {
      int index = j+i*10;
      sprintf(newtable+index, "%s", wordtable[i][j].get<std::string>().c_str());
    }
  }
  wt.set_table(newtable);

  for(int i=0; i<10; i++) {
    for(int j=0; j<10; j++) {
      wordvector temp;
      wc.resize(0);
      solve(i, j, 5, temp);
      std::sort( wc.begin(), wc.end() );
      wc.erase( std::unique( wc.begin(), wc.end() ), wc.end() );
      for(const auto & candidate : wc) {
	if(wt.check_validity(candidate)) {
	  if(wl.is_word(wt.get_word(candidate))) {    
	    std::cout << " - " << wt.get_word(candidate) << "\n";
	    url = "https://localhost:8088/checkword";
	    json jcand = candidate;
	    jii = {{"word", jcand.dump()},{"key", sessionkey}};
	    data = jii.dump();
	    if(access.put((char *)(url.c_str()), (char *)data.c_str()) == false) {
	      fprintf(stderr, "Connection failed\n");
	      exit(EXIT_FAILURE);
	    }
	    jii = json::parse(access.read());
	    std::cout << "\nGot status: " << jii << "\n";
	  }
	}
      }
    }
  }
   
  return EXIT_SUCCESS;
}
