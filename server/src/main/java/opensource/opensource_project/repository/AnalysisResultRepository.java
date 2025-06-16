package opensource.opensource_project.repository;

import opensource.opensource_project.domain.analysis_result.entity.AnalysisResult;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AnalysisResultRepository extends JpaRepository<AnalysisResult, Long> {

}
