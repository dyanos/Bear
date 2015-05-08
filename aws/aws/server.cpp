#include "crow_all.h"
#include "AWSFastDB.h"
#include "AWSLocationDB.h"

#include <iostream>

#include <unordered_map>

#ifdef _DEBUG
#include <typeinfo>
#endif

int main() {
  AWSFastDB db;
  AWSLocationDB locdb;

  crow::SimpleApp app;

  // aws의 정보들을 읽어들인다.
  locdb.load("awsinfo");

  CROW_ROUTE(app, "/reload") 
  ([]() {
    // aws 정보를 다시 읽어들인다.
    return crow::response(200);
  });

  CROW_ROUTE(app, "/ping")
  ([]() {
    return crow::response(200);
  });

  CROW_ROUTE(app, "/push/aws").methods("POST"_method)
  ([&](const crow::request& req) {
    auto it = req.headers.find("Content-Type");

    std::string type = "";
    if (it == req.headers.end()) {
      type = "application/json";
    }
    else {
      type = it->second;
    }

#ifdef _DEBUG
    std::cout << "type : " << type << std::endl;
#endif

    if (type == "application/json" || type == "text/json") {
      auto d = crow::json::load(req.body);

      if (!d) 
        return crow::response(404);

      if (d.has("data") == false || d.has("ndata") == false) {
#ifdef _DEBUG
        std::cout << "no data or ndata found" << std::endl;
#endif
        return crow::response(404);
      }

      for (auto& dt : d["data"]) {
        std::string dtstr = dt["tm"].s();
        auto awsno = dt["pt_no"].i();
#ifdef _DEBUG
        std::cout << "tm : " << dtstr << ", awsno : " << awsno << ", type of dt : " << typeid(dt).name() << std::endl;
#endif
        std::ostringstream os;
        os << awsno;
        std::string _awsno = os.str();
        db.insert(_awsno, dtstr, dt);
      } 

      return crow::response(200);
    }

    return crow::response(404);
  });

  CROW_ROUTE(app, "/query/aws").methods("GET"_method)
  ([&db, &locdb](const crow::request& req) {
#ifdef _DEBUG
    std::cout << "calling request /query/aws" << std::endl;
#endif

    auto& params = req.url_params;

    double lat = 0., lng = 0.;

    auto t = params.get("lat");
    if (t == nullptr) {
#ifdef _DEBUG
      std::cout << "no lat parameter" << std::endl;
#endif
      return crow::response(404);
    }
    lat = ::atof(t);
    
    t = params.get("lng");
    if (t == nullptr) {
#ifdef _DEBUG
      std::cout << "no lng parameter" << std::endl;
#endif
      return crow::response(404);
    }
    lng = ::atof(t);

#ifdef _DEBUG
    std::cout << lat << ":" << lng << std::endl;
#endif

    auto dt = params.get("datetime");
    if (dt == nullptr) {
#ifdef _DEBUG
      std::cout << "no datetime parameter" << std::endl;
#endif 
      return crow::response(404);
    }

    auto awsno = locdb.search(lat, lng);
    crow::json::rvalue* r = nullptr;
    for (auto& val : awsno) {
      std::ostringstream os;
      os << val << ":" << dt;
      std::string s = os.str();
      r = db.find(s);
#ifdef _DEBUG
      std::cout << "key : " << s << ", " << *r << std::endl;
#endif
      if (r != nullptr) {
        break;
      }
    }

    // 오류 체크 코드를 넣어두어야 한다.
    if (r == nullptr) {
#ifdef _DEBUG
      std::cout << "not found" << std::endl;
#endif
      return crow::response(404);
    }

    return crow::response(*r); 
  });

#ifdef _TEST_DEBUG
  CROW_ROUTE(app, "/test/query/awsno").methods("GET"_method) 
  ([&](const crow::request& req) {
    auto& params = req.url_params;

    std::cout << params << std::endl;

    double lat = 0., lng = 0.;

    auto t = params.get("lat");
    if (t == nullptr) {
      return crow::response(404);
    }
    lat = ::atof(t);
    
    t = params.get("lng");
    if (t == nullptr) {
      return crow::response(404);
    }
    lng = ::atof(t);

    crow::json::wvalue ret;
    ret["lat"] = lat;
    ret["lng"] = lng;
 
    auto awsno = locdb.search(lat, lng);
    if (awsno.size() > 0) {
      ret["awsno"] = awsno[0];
    }

    return crow::response(ret);
  });
#endif

  app.port(18080)
     .multithreaded()
     .run();
  
  return 0;
}
