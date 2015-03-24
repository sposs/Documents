std::map< float, std::list< std::pair < std::string, double > > > a;
std::pair< std::string, double > item ("key", 23.5);
std::list< std::pair< std::string, double > > my_list (item);
//be carefull with >> vs > >
a[21.] = my_list;

