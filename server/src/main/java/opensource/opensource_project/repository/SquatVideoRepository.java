package opensource.opensource_project.repository;

import opensource.opensource_project.domain.squat_videos.entity.SquatVideo;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface SquatVideoRepository extends JpaRepository<SquatVideo, Long> {

}
