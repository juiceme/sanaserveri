/*

Encapsulates word list handling.

Requires that there are prepared wordlists words3...words10 for
valid words containig 3 to 10 letters in the run directory.

*/

#ifndef INCLUDE_WORDLIST_HPP_
#define INCLUDE_WORDLIST_HPP_

#include <iostream>
#include <fstream>
#include <string>
#include <vector>

class WordList {

public:

  WordList() {
    std::ifstream fstream;
    std::string filename, word;
    for(int i=3; i<11; i++) {
      filename = "words" + std::to_string(i);
      fstream.open(filename);
      if (!fstream) {
	std::cerr << "Failed to open dictionary words" << i << "\n";
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

#endif  // INCLUDE_WORDLIST_HPP
