if ( (val > 2 && val < 5) || val2){
   std::cout << val << std::endl;
}

it = map.find("key");
if (it != map.end() && NULL != it){
   std::cout << it->second << std::endl;
}
