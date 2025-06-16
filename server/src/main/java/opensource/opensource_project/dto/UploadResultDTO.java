package opensource.opensource_project.dto;
import lombok.Getter;
import lombok.Setter;
import org.springframework.stereotype.Component;

@Getter
@Setter
public class UploadResultDTO {

    public UploadResultDTO(String originalFileName, String s3Url, String extension) {
        this.originalFileName = originalFileName;
        this.s3Url = s3Url;
        this.extension = extension;
    }

    private String originalFileName;
    private String s3Url;
    private String extension;
}
