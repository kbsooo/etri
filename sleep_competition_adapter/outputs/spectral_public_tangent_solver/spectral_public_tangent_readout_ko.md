# Spectral Public-Tangent Solver

## 핵심 주장

H057 이후 public에서 나빠진 submission들은 독립적인 실패가 아니라 하나의 저차원 public-loss tangent를 공유한다. HS-JEPA action이 진짜라면 이 bad tangent의 반대 방향 또는 거의 직교한 subspace에서 release되어야 한다.

## Spectral 진단

- public anchor count: `26`
- first mode variance: `0.962855`
- top5 cumulative variance: `0.994683`
- mean bad-tangent coordinate: `0.750007`

## 후보

| rank | variant | changed cells | rows | bad dot | bad cosine | upload safe | file |
| ---: | --- | ---: | ---: | ---: | ---: | --- | --- |
| 1 | `anti_bad_tangent_pressure` | `64` | `56` | `-0.327559` | `-0.0964` | `True` | `submission_hsjepa_spectral_public_tangent_anti_bad_tangent_pressure_6a93251a_uploadsafe.csv` |
| 2 | `anti_bad_tangent_sparse` | `32` | `30` | `-0.077088` | `-0.0407` | `True` | `submission_hsjepa_spectral_public_tangent_anti_bad_tangent_sparse_dda70077_uploadsafe.csv` |
| 3 | `bad_tangent_sign_flip` | `3` | `3` | `-0.034708` | `-0.0803` | `True` | `submission_hsjepa_spectral_public_tangent_bad_tangent_sign_flip_8ff80d37_uploadsafe.csv` |
| 4 | `orthogonal_private_residual` | `25` | `21` | `-0.001439` | `-0.0009` | `True` | `submission_hsjepa_spectral_public_tangent_orthogonal_private_residual_57ed54c2_uploadsafe.csv` |

## Public LB 해석

- anti-bad 후보가 좋아지면: H057 이후 plateau는 public-bad tangent의 반대 방향을 충분히 못 탄 것이다.
- orthogonal 후보가 좋아지면: H057는 public tangent상 거의 최적이고, 남은 upside는 private-safe residual subspace에 있다.
- sign-flip 후보가 좋아지면: cell support는 맞았지만 action sign equation이 틀렸다는 뜻이다.
- 모두 나빠지면: public 실패들의 low-rank 구조는 real이지만, 그 반대 방향이 label-valid action이라는 보장은 없다는 뜻이다.