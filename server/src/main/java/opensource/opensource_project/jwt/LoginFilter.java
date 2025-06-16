package opensource.opensource_project.jwt;

import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.FilterChain;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import opensource.opensource_project.domain.refresh_token.entity.Refresh;
import opensource.opensource_project.dto.CustomUserDetails;
import opensource.opensource_project.dto.LoginDTO;
import opensource.opensource_project.repository.RefreshRepository;
import org.springframework.http.HttpStatus;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.AuthenticationServiceException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

import java.io.IOException;
import java.util.Collection;
import java.util.Date;
import java.util.Iterator;

public class LoginFilter extends UsernamePasswordAuthenticationFilter {

    private final AuthenticationManager authenticationManager;
    private final JwtUtil jwtUtil;
    private final RefreshRepository refreshRepository;

    public LoginFilter(AuthenticationManager authenticationManager, JwtUtil jwtUtil, RefreshRepository refreshRepository) {
        this.authenticationManager = authenticationManager;
        this.jwtUtil = jwtUtil;
        this.refreshRepository = refreshRepository;
    }

    @Override
    public Authentication attemptAuthentication(HttpServletRequest request, HttpServletResponse response) throws AuthenticationException {
        try {
            // JSON 요청 처리
            if (request.getContentType() != null && request.getContentType().contains("application/json")) {
                ObjectMapper objectMapper = new ObjectMapper();
                LoginDTO loginDTO = objectMapper.readValue(request.getInputStream(), LoginDTO.class);

                String username = loginDTO.getUsername();
                String password = loginDTO.getPassword();

                UsernamePasswordAuthenticationToken authToken = new UsernamePasswordAuthenticationToken(username, password, null);
                return authenticationManager.authenticate(authToken);
            } else {
                // 기존 form-data 처리
                String username = obtainUsername(request);
                String password = obtainPassword(request);

                UsernamePasswordAuthenticationToken authToken = new UsernamePasswordAuthenticationToken(username, password, null);
                return authenticationManager.authenticate(authToken);
            }
        } catch (IOException e) {
            throw new AuthenticationServiceException("요청 파싱 실패", e);
        }
    }


    @Override
    protected void successfulAuthentication (HttpServletRequest request, HttpServletResponse response, FilterChain chain, Authentication authentication) {
        //유저 정보
        CustomUserDetails customUserDetails = (CustomUserDetails) authentication.getPrincipal();
        String username = customUserDetails.getUsername();
        String realName = customUserDetails.getRealName();

        Collection<? extends GrantedAuthority> authorities = customUserDetails.getAuthorities();
        Iterator<? extends GrantedAuthority> iterator = authorities.iterator();
        GrantedAuthority authority = iterator.next();

        String role = authority.getAuthority();

        //토큰 생성
        String access = jwtUtil.createJwt("access", username, role, realName, 1000L * 60 * 30);
        String refresh = jwtUtil.createJwt("refresh", username, role, realName, 1000L * 60 * 60 * 24 * 30);

        //refresh 토큰 저장
        addRefreshEntity(username, refresh, 1000L * 60 * 60 * 24 * 30);

        //응답 설정
        response.setHeader("access", access);
        response.addCookie(createCookie("refresh", refresh));
        response.setStatus(HttpStatus.OK.value());
    }

    private void addRefreshEntity(String username, String refresh, Long expireMs) {
        Date date = new Date(System.currentTimeMillis() + expireMs);

        Refresh refreshToken = new Refresh();
        refreshToken.setUsername(username);
        refreshToken.setRefresh(refresh);
        refreshToken.setExpiration(date.toString());

        refreshRepository.save(refreshToken);
    }

    private Cookie createCookie(String key, String value) {
        Cookie cookie = new Cookie(key, value);
        cookie.setMaxAge(24*60*60*30);
        cookie.setSecure(true);
        cookie.setHttpOnly(true);
        cookie.setPath("/");

        return cookie;
    }

    @Override
    protected void unsuccessfulAuthentication (HttpServletRequest request, HttpServletResponse response, AuthenticationException failed) {
        response.setStatus(401);
        response.setHeader("error", failed.getMessage());
    }
}
