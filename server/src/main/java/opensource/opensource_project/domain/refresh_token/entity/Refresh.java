package opensource.opensource_project.domain.refresh_token.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import opensource.opensource_project.domain.user.entity.User;

@Entity
@Table(name = "refresh")
@Getter
@Setter
public class Refresh {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long refreshId;

    @Column
    private String username;

    @Column
    private String refresh;

    @Column
    private String expiration;
}
