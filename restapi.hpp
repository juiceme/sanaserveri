/*

Encapsulates REST API for sanaerveri.
Needs to be compiled with "-L/opt/curl/lib -lcurl"

*/

#ifndef INCLUDE_RESTAPI_HPP_
#define INCLUDE_RESTAPI_HPP_

#include <curl/curl.h>

class RestApi {

public:

  RestApi() {
    curl_global_init(CURL_GLOBAL_DEFAULT);
    conn = curl_easy_init();
    if(conn == NULL) {
      std::cerr << "Failed to create CURL connection\n";
      exit(EXIT_FAILURE);
    }
  }

  ~RestApi() {
    curl_easy_cleanup(conn);
  }

  int get(char* url, char* data) {
    CURLcode code;
    struct curl_slist *headers=NULL;

    code = curl_easy_setopt(conn, CURLOPT_ERRORBUFFER, errorBuffer);
    if(code != CURLE_OK) {
      std::cerr << "Failed to set error buffer [" << code << "]\n";
      return false;
    }
    headers = curl_slist_append(headers, "Content-Type: application/json");
    code = curl_easy_setopt(conn, CURLOPT_HTTPHEADER, headers);
    if(code != CURLE_OK) {
      std::cerr << "Failed to set http headers, [" << code << "]\n";
      return false;
    }
    code = curl_easy_setopt(conn, CURLOPT_URL, url);
    if(code != CURLE_OK) {
      std::cerr << "Failed to set URL " << url << " [" << errorBuffer << "]\n";
      return false;
    }
    code = curl_easy_setopt(conn, CURLOPT_CUSTOMREQUEST, "GET");
    if(code != CURLE_OK) {
      std::cerr << "Failed to set curl to put request mode [" << code << "]\n";
      return false;
    }
    code = curl_easy_setopt(conn, CURLOPT_POSTFIELDS, data);
    if(code != CURLE_OK) {
      std::cerr << "Failed to set post data, [" << code << "]\n";
      return false;
    }
    code = curl_easy_setopt(conn, CURLOPT_CAINFO, "./cert.pem");
    if(code != CURLE_OK) {
      std::cerr << "Failed to trust selfsigned certs\n";
      return false;
    }
    code = curl_easy_setopt(conn, CURLOPT_SSL_VERIFYHOST, 0);
    if(code != CURLE_OK) {
      std::cerr << "Failed to set verifyhost\n";
      return false;
    }
    code = curl_easy_setopt(conn, CURLOPT_FOLLOWLOCATION, 1L);
    if(code != CURLE_OK) {
      std::cerr << "Failed to set redirect option [" << errorBuffer << "]\n";
      return false;
    }
    code = curl_easy_setopt(conn, CURLOPT_WRITEFUNCTION, RestApi::writer);
    if(code != CURLE_OK) {
      std::cerr << "Failed to set writer [" << errorBuffer << "]\n";
      return false;
    }
    code = curl_easy_setopt(conn, CURLOPT_WRITEDATA, &buffer);
    if(code != CURLE_OK) {
      std::cerr << "Failed to set write data [" << errorBuffer << "]\n";
      return false;
    }
    buffer = "";
    code = curl_easy_perform(conn);
    if(code != CURLE_OK) {
      std::cerr << "Failed to start session, [" << errorBuffer << "]\n";
      return false;
    }
    return true;
  }

  int put(char* url, char* data) {
    CURLcode code;
    struct curl_slist *headers=NULL;

    code = curl_easy_setopt(conn, CURLOPT_ERRORBUFFER, errorBuffer);
    if(code != CURLE_OK) {
      std::cerr << "Failed to set error buffer [" << code << "]\n";
      return false;
    }
    headers = curl_slist_append(headers, "Content-Type: application/json");
    code = curl_easy_setopt(conn, CURLOPT_HTTPHEADER, headers);
    if(code != CURLE_OK) {
      std::cerr << "Failed to set http headers, [" << code << "]\n";
      return false;
    }
    code = curl_easy_setopt(conn, CURLOPT_URL, url);
    if(code != CURLE_OK) {
      std::cerr << "Failed to set URL " << url << " [" << errorBuffer << "]\n";
      return false;
    }
    code = curl_easy_setopt(conn, CURLOPT_CUSTOMREQUEST, "PUT");
    if(code != CURLE_OK) {
      std::cerr << "Failed to set curl to put request mode [" << code << "]\n";
      return false;
    }
    code = curl_easy_setopt(conn, CURLOPT_POSTFIELDS, data);
    if(code != CURLE_OK) {
      std::cerr << "Failed to set post data, [" << code << "]\n";
      return false;
    }
    code = curl_easy_setopt(conn, CURLOPT_CAINFO, "./cert.pem");
    if(code != CURLE_OK) {
      std::cerr << "Failed to trust selfsigned certs\n";
      return false;
    }
    code = curl_easy_setopt(conn, CURLOPT_SSL_VERIFYHOST, 0);
    if(code != CURLE_OK) {
      std::cerr << "Failed to set verifyhost\n";
      return false;
    }
    code = curl_easy_setopt(conn, CURLOPT_FOLLOWLOCATION, 1L);
    if(code != CURLE_OK) {
      std::cerr << "Failed to set redirect option [" << errorBuffer << "]\n";
      return false;
    }
    code = curl_easy_setopt(conn, CURLOPT_WRITEFUNCTION, writer);
    if(code != CURLE_OK) {
      std::cerr << "Failed to set writer [" << errorBuffer << "]\n";
      return false;
    }
    code = curl_easy_setopt(conn, CURLOPT_WRITEDATA, &buffer);
    if(code != CURLE_OK) {
      std::cerr << "Failed to set write data [" << errorBuffer << "]\n";
      return false;
    }
    buffer = "";
    code = curl_easy_perform(conn);
    if(code != CURLE_OK) {
      std::cerr << "Failed to start session, [" << errorBuffer << "]\n";
      return false;
    }
    return true;
  }

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

#endif  // INCLUDE_RESTAPI_HPP_
