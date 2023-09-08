#include <iostream>
#include <fstream>
using namespace std;

int main(){
    ofstream file;
    string name;
    cout << "bwrian fwucky v1" << endl; 
    
    cout << "uwhat iws da name of the fwile?" << endl; 
    cin >> name;
    file.open(name + ".b");

    cout << "uwhat do youwu uwant to uwurite?" << endl; 
    string input;
    cin >> input;
    
    int i;
    string output = "";
    for(i=0;i<input.length();i++){
        output += string(input[i], '+') + ".>";
    }

    
    file << output;
    cout << "youwur fwile iws saved teehee~" << endl; 
    file.close();
    return 0;
}