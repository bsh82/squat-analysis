package opensource.opensource_project.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ResponseBody;

@Controller
@ResponseBody
public class AdminConstoller {

    @GetMapping("/admin")
    public String admin() {
        return "admin";
    }
}
