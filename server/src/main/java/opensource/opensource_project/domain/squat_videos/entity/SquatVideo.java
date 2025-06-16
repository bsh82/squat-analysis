package opensource.opensource_project.domain.squat_videos.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import opensource.opensource_project.domain.squat_videos.squat_video_constants.Status;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

@Entity
@Table(name = "squat_video")
@Getter
@Setter
public class SquatVideo {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long videoId;

    @Column(name = "username", nullable = false)
    private String username;

    @Column(name = "original_filename", length = 255)
    private String originalFilename;

    @Column
    private String extension;

    @Column(name = "s3_url", nullable = false, columnDefinition = "TEXT")
    private String s3Url;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Status status;

    @CreationTimestamp
    @Column(name = "uploaded_at", updatable = false)
    private LocalDateTime uploadedAt;
}