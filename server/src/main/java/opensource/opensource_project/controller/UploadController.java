package opensource.opensource_project.controller;

import jakarta.servlet.http.HttpServletRequest;
import opensource.opensource_project.domain.analysis_result.entity.AnalysisResult;
import opensource.opensource_project.domain.squat_videos.entity.SquatVideo;
import opensource.opensource_project.domain.squat_videos.squat_video_constants.Status;
import opensource.opensource_project.dto.CustomUserDetails;
import opensource.opensource_project.dto.UploadResponseDTO;
import opensource.opensource_project.dto.UploadResultDTO;
import opensource.opensource_project.repository.AnalysisResultRepository;
import opensource.opensource_project.repository.SquatVideoRepository;
import opensource.opensource_project.service.VideoUploadService;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.core.io.InputStreamResource;
import org.springframework.http.*;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.HttpServerErrorException;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.multipart.MultipartRequest;

import java.io.IOException;
import java.util.List;
import java.util.Map;

@Controller
@ResponseBody
@Transactional
public class UploadController {
    private final VideoUploadService videoUploadService;
    private SquatVideoRepository squatVideoRepository;
    private AnalysisResultRepository analysisResultRepository;

    public UploadController(VideoUploadService videoUploadService, SquatVideoRepository squatVideoRepository, AnalysisResultRepository analysisResultRepository) {
        this.videoUploadService = videoUploadService;
        this.squatVideoRepository = squatVideoRepository;
        this.analysisResultRepository = analysisResultRepository;
    }

    @PostMapping("/upload")
    public ResponseEntity<?> upload(MultipartRequest request) throws Exception {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        CustomUserDetails userDetails = (CustomUserDetails) authentication.getPrincipal();

        UploadResultDTO uploadResult = null;

        try {
            uploadResult = videoUploadService.videoUploadProcess(request);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }

        String username = userDetails.getUsername();
        String fileName = uploadResult.getOriginalFileName();
        String s3Url = uploadResult.getS3Url();
        String extension = uploadResult.getExtension();
        Status status = Status.FAILED;

        SquatVideo data1 = new SquatVideo();

        data1.setUsername(username);
        data1.setOriginalFilename(fileName);
        data1.setS3Url(s3Url);
        data1.setExtension(extension);
        data1.setStatus(status);

        //DB에 meta data 저장
        SquatVideo savedData = squatVideoRepository.save(data1);
        Long videoId = savedData.getVideoId();

        //분석 서버로 영상 데이터 전송 - InputStreamResource 문제 해결
        MultipartFile file = request.getFile("upload");

        // ByteArrayResource로 변경하여 스트림 재사용 문제 해결
        byte[] fileBytes = file.getBytes();
        ByteArrayResource resource = new ByteArrayResource(fileBytes) {
            @Override
            public String getFilename() {
                return file.getOriginalFilename();
            }
        };

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("file", resource);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        RestTemplate restTemplate = new RestTemplate();

        HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);
        try {
            ResponseEntity<Map> response = restTemplate.postForEntity("http://localhost:8000/analyze", requestEntity, Map.class);

            // 응답 상태 코드 확인
            if (!response.getStatusCode().is2xxSuccessful()) {
                throw new RuntimeException("분석 서버 응답 실패: " + response.getStatusCode());
            }

            Map<String, Object> responseBody = response.getBody();

            if (responseBody == null) {
                throw new RuntimeException("분석 서버로부터 응답 데이터가 없습니다");
            }

            // 타입 안전성 개선
            Object scoreObj = responseBody.get("score");
            Float score = null;
            if (scoreObj instanceof Number) {
                score = ((Number) scoreObj).floatValue();
            }

            List<String> feedbackList = (List<String>) responseBody.get("feedback");
            String feedback = "";

            if (feedbackList != null && !feedbackList.isEmpty()) {
                feedback = String.join("\n", feedbackList);
            }

            AnalysisResult data2 = new AnalysisResult();
            data2.setUsername(username);
            data2.setVideoId(videoId);
            data2.setScore(score);
            data2.setFeedback(feedback);

            analysisResultRepository.save(data2);

            // 분석 성공 시에만 status를 DONE 변경
            savedData.setStatus(Status.DONE);
            squatVideoRepository.save(savedData);

            UploadResponseDTO responseDTO = new UploadResponseDTO();
            responseDTO.setFeedBack(feedback);
            responseDTO.setScore(score);

            return ResponseEntity.ok(responseDTO);

        } catch (ResourceAccessException e) {
            // 네트워크 연결 실패 (서버가 응답하지 않음)
            System.err.println("분석 서버 연결 실패: " + e.getMessage());

            // 실패 정보를 DB에 기록
            AnalysisResult failedResult = new AnalysisResult();
            failedResult.setUsername(username);
            failedResult.setVideoId(videoId);
            failedResult.setScore(null);
            failedResult.setFeedback("분석 서버 연결 실패");
            analysisResultRepository.save(failedResult);

            // status는 이미 FAILED로 설정되어 있으므로 그대로 유지

            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("분석 서버에 연결할 수 없습니다");

        } catch (HttpClientErrorException e) {
            // 4xx 에러 (클라이언트 요청 오류)
            System.err.println("분석 요청 오류: " + e.getStatusCode() + " - " + e.getResponseBodyAsString());

            AnalysisResult failedResult = new AnalysisResult();
            failedResult.setUsername(username);
            failedResult.setVideoId(videoId);
            failedResult.setScore(null);
            failedResult.setFeedback("분석 요청 오류: " + e.getStatusCode());
            analysisResultRepository.save(failedResult);

            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body("분석 요청이 잘못되었습니다");

        } catch (HttpServerErrorException e) {
            // 5xx 에러 (서버 내부 오류)
            System.err.println("분석 서버 내부 오류: " + e.getStatusCode() + " - " + e.getResponseBodyAsString());

            AnalysisResult failedResult = new AnalysisResult();
            failedResult.setUsername(username);
            failedResult.setVideoId(videoId);
            failedResult.setScore(null);
            failedResult.setFeedback("분석 서버 내부 오류");
            analysisResultRepository.save(failedResult);

            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("분석 서버에서 오류가 발생했습니다");

        } catch (Exception e) {
            // 기타 예상치 못한 오류
            System.err.println("예상치 못한 오류: " + e.getMessage());

            AnalysisResult failedResult = new AnalysisResult();
            failedResult.setUsername(username);
            failedResult.setVideoId(videoId);
            failedResult.setScore(null);
            failedResult.setFeedback("분석 중 오류 발생");
            analysisResultRepository.save(failedResult);

            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("분석 처리 중 오류가 발생했습니다");
        }
    }
}
