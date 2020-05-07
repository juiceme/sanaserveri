/*

Encapsulates word table handling.

*/

#ifndef INCLUDE_WORDTABLE_HPP_
#define INCLUDE_WORDTABLE_HPP_

#include <string>
#include <vector>
#include <tuple>
#include <algorithm>

class WordTable {

public:

  typedef std::vector< std::tuple<int, int> > wordvector;
  typedef std::vector< wordvector > wordvectorlist;

  WordTable() {
    my_table = create_table();
  }

  ~WordTable() {
    if(my_table != NULL) {
      free(my_table);
      my_table = NULL;
    }
  }

  void set_table(char* table) {
    free(my_table);
    my_table = table;
  }

  std::string get_word(wordvector wv) {
    std::string word;
    for(const auto & element : wv) {
      int x = std::get<0>(element);
      int y = std::get<1>(element);
      int index = y+x*10;
      word.append(1, static_cast<char>(my_table[index]));
    }
    return word;
  }

  bool check_validity(wordvector wv) {
    wordvector copywv = wv;
    std::sort( wv.begin(), wv.end() );
    wordvector::iterator it = std::unique( copywv.begin(), copywv.end() );
    if(it != copywv.end()) {
      return false;
    }
    for(const auto & element : wv) {
      if(std::get<0>(element) < 0 || std::get<0>(element) > 9 ||
	 std::get<1>(element) < 0 || std::get<1>(element) > 9) {
	return false;
      }
    }
    int x0=10, y0=10, xdiff=0, ydiff=0;
    for(const auto & element : wv) {
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
    char* table = (char*) malloc(sizeof(char[100]));
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

#endif  // INCLUDE_WORDTABLE_HPP
