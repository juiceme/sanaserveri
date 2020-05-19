/*
 * compile with:
 * g++ -Wall -I/opt/curl/include solverbot2.cpp -o solverbot2 -L/opt/curl/lib -lcurl
 *
 */

#include "json.hpp"
#include "wordlist.hpp"
#include "wordtable.hpp"
#include "restapi.hpp"

using json = nlohmann::json;

WordTable::wordvectorlist wc;

void solve(int i, int j, int depth, WordTable::wordvector wv) {
  if(depth == 0) {
    wc.push_back(wv);
    return;
  } else {
    wv.push_back(std::make_tuple(i,j));
    solve(i, j-1, depth-1, wv);
    solve(i, j+1, depth-1, wv);
    solve(i-1, j, depth-1, wv);
    solve(i+1, j, depth-1, wv);    
  }
}

int main(int argc, char *argv[])
{
  WordList wl;
  WordTable wt;
  RestApi rest_api;
  std::string url, data;
  json jii;

  url = "https://localhost:8088/startsession";
  if(rest_api.get((char *)(url.c_str()), (char *)"") == false) {
    fprintf(stderr, "Connection failed\n");
    exit(EXIT_FAILURE);
  }
  jii = json::parse(rest_api.read());
  if(jii["status"] != "OK") {
    fprintf(stderr, "Failed to get session key\n");
    exit(EXIT_FAILURE);
  }
  auto sessionkey = jii["key"].get<std::string>();
  std::cout << "Got session key: " << sessionkey << "\n";

  url = "https://localhost:8088/login";
  jii = {{"username", "solverbot2"},{"password", "50lver80t"},{"key", sessionkey}};
  data = jii.dump();
  if(rest_api.put((char *)(url.c_str()), (char *)data.c_str()) == false) {
    fprintf(stderr, "Connection failed\n");
    exit(EXIT_FAILURE);
  }
  jii = json::parse(rest_api.read());
  if(jii["status"] != "OK") {
    fprintf(stderr, "Failed to log in\n");
    exit(EXIT_FAILURE);
  }
  std::cout << "Logged in to server\n";

  url = "https://localhost:8088/getwords";
  jii = {{"key", sessionkey}};
  data = jii.dump();
  if(rest_api.get((char *)(url.c_str()), (char *)data.c_str()) == false) {
    fprintf(stderr, "Connection failed\n");
    exit(EXIT_FAILURE);
  }
  jii = json::parse(rest_api.read());
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
      WordTable::wordvector temp;
      wc.resize(0);
      solve(i, j, 5, temp);
      std::sort( wc.begin(), wc.end() );
      wc.erase( std::unique( wc.begin(), wc.end() ), wc.end() );
      for(const auto & candidate : wc) {
	if(wt.check_validity(candidate)) {
	  if(wl.is_word(wt.get_word(candidate))) {
	    json jcand = candidate;
	    std::cout << jcand << " - " << wt.get_word(candidate) << "\n";
	    url = "https://localhost:8088/checkword";
	    jii = {{"word", jcand.dump()},{"key", sessionkey}};
	    data = jii.dump();
	    if(rest_api.put((char *)(url.c_str()), (char *)data.c_str()) == false) {
	      fprintf(stderr, "Connection failed\n");
	      exit(EXIT_FAILURE);
	    }
	    jii = json::parse(rest_api.read());
	    std::cout << "Got status: " << jii << "\n\n";
	  }
	}
      }
    }
  }

  url = "https://localhost:8088/stopsession";
  jii = {{"key", sessionkey}};
  data = jii.dump();
  if(rest_api.get((char *)(url.c_str()), (char *)data.c_str()) == false) {
    fprintf(stderr, "Connection failed\n");
    exit(EXIT_FAILURE);
  }
  jii = json::parse(rest_api.read());
  if(jii["status"] != "OK") {
    fprintf(stderr, "Failed to stop session\n");
    exit(EXIT_FAILURE);
  }
  std::cout << "Stopped session\n";
   
  return EXIT_SUCCESS;
}
