package opensource.opensource_project.service;

import opensource.opensource_project.domain.user.entity.User;
import opensource.opensource_project.dto.JoinDTO;
import opensource.opensource_project.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class JoinService {

    private final UserRepository userRepository;
    private final BCryptPasswordEncoder bCryptPasswordEncoder;

    @Autowired
    public JoinService(UserRepository userRepository, BCryptPasswordEncoder bCryptPasswordEncoder) {
        this.userRepository = userRepository;
        this.bCryptPasswordEncoder = bCryptPasswordEncoder;
    }

    public void joinProcess(JoinDTO joinDTO) {
        String username = joinDTO.getUsername();
        String password = joinDTO.getPassword();
        String realName = joinDTO.getRealName();

        Boolean isExist = userRepository.existsByUsername(username);

        if(isExist) {
            return;
        }

        User data = new User();

        data.setUsername(username);
        data.setPassword(bCryptPasswordEncoder.encode(password));
        data.setRealName(realName);
        data.setRole("ROLE_USER");

        userRepository.save(data);
    }
}
