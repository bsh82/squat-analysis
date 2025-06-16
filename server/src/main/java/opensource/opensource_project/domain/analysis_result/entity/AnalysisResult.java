package opensource.opensource_project.domain.analysis_result.entity;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import opensource.opensource_project.domain.squat_videos.entity.SquatVideo;
import opensource.opensource_project.domain.user.entity.User;
import org.hibernate.annotations.CreationTimestamp;
import java.time.LocalDateTime;

@Entity
@Table(name = "analysis_result")
@Getter
@Setter
public class AnalysisResult {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long analysisId;

    @Column(nullable = false)
    private Long videoId;

    @Column(nullable = false)
    private String username;

    @Column(columnDefinition = "TEXT")
    private String feedback;

    @Column
    private Float score;

    @CreationTimestamp
    @Column(name = "analyzed_at", updatable = false)
    private LocalDateTime analyzedAt;
}
