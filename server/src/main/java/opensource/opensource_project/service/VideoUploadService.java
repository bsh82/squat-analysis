package opensource.opensource_project.service;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.ObjectMetadata;
import com.amazonaws.services.s3.model.PutObjectRequest;
import opensource.opensource_project.config.S3Config;
import opensource.opensource_project.dto.UploadResultDTO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.multipart.MultipartRequest;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.util.UUID;

@Service
public class VideoUploadService {
    private final AmazonS3 amazonS3Client;

    @Value("${cloud.aws.s3.bucket}")
    private String bucket;

    @Autowired
    public VideoUploadService(AmazonS3 amazonS3Client) {
        this.amazonS3Client = amazonS3Client; // S3Config 대신 직접 주입
    }

    public UploadResultDTO videoUploadProcess(MultipartRequest request) throws IOException {
        MultipartFile file = request.getFile("upload");

        if (file == null || file.isEmpty()) {
            throw new IllegalArgumentException("업로드할 파일이 없습니다.");
        }

        String fileName = file.getOriginalFilename();
        if (fileName == null) {
            throw new IllegalArgumentException("파일명을 확인할 수 없습니다.");
        }

        String extension = fileName.substring(fileName.lastIndexOf("."));
        String uuidFileName = UUID.randomUUID() + extension;

        // 스트림으로 직접 S3에 업로드 (임시 파일 생성 없음)
        try (InputStream inputStream = file.getInputStream()) {
            ObjectMetadata metadata = new ObjectMetadata();
            metadata.setContentLength(file.getSize());
            metadata.setContentType(file.getContentType());

            PutObjectRequest putObjectRequest = new PutObjectRequest(
                    bucket,
                    uuidFileName,
                    inputStream,
                    metadata
            );

            amazonS3Client.putObject(putObjectRequest);
        }

        String s3Url = amazonS3Client.getUrl(bucket, uuidFileName).toString();

        return new UploadResultDTO(fileName, s3Url, extension);
    }
}