# OpenWorld

**Bộ công cụ nghiên cứu cục bộ cho các agent có trí nhớ, biết thích nghi và hợp tác.**

OpenWorld nghiên cứu cách xây dựng những agent AI có danh tính lâu dài, lưu được bằng chứng về hoạt động của mình, học từ tương tác và hợp tác trong giới hạn tài nguyên rõ ràng. Mục tiêu dài hạn là một hệ sinh thái agent mở. Hiện tại, dự án là **bộ công cụ thử nghiệm bằng Python, chạy trên CPU**, gồm thế giới mô phỏng và các thí nghiệm có thể chạy lại để kiểm chứng.

Mỗi agent có danh tính, lịch sử, trạng thái và quyền truy cập riêng. Nhiều agent có thể dùng chung một mô hình AI; không cần tạo một mô hình nền tảng riêng cho từng agent.

**Trạng thái:** bản thử nghiệm nghiên cứu, chưa sẵn sàng vận hành thực tế. Các thí nghiệm đi kèm không cần GPU, khóa API mô hình hay dịch vụ trả phí.

## Bắt đầu nhanh

Yêu cầu **Python 3.11 trở lên**. Các bài kiểm tra và ví dụ mặc định sử dụng thư viện chuẩn của Python. Phần thử nghiệm PostgreSQL tùy chọn có yêu cầu cài đặt riêng.

```bash
git clone https://github.com/iamphan04/OpenWorld.git
cd OpenWorld

# Chạy một thế giới nhỏ có thể phát lại để kiểm chứng.
python examples/world/demo.py --agents 30 --ticks 20

# Kiểm tra cấu trúc dự án và chạy bộ kiểm thử.
python scripts/check_repository.py
python -m unittest discover -s tests -v
```

Ví dụ trao đổi giữa ba nhóm agent thuộc cùng một chủ sở hữu:

```bash
python examples/populations/local_three_groups.py
```

Chạy các lệnh từ thư mục gốc của dự án. Những ví dụ này dùng agent và sự kiện mô phỏng, không gọi mô hình ngôn ngữ và không kết nối với thế giới của chủ sở hữu khác.

## Chạy mô phỏng đúng hai agent bằng Python

[Chương trình hai agent](examples/two_agents.py) tạo A và B, chạy từng lượt và in diễn biến trực tiếp trong terminal:

- **A** quyết định có gửi một đơn vị tài nguyên hay không, theo dõi hạn mức và xử lý phản hồi.
- **B** nhận tài nguyên rồi quyết định trả lại hoặc giữ, tùy kịch bản.
- Thế giới W3 ghi lại các lần chuyển. Thông báo cho A có thể bị chậm hoặc mất; biên nhận chính xác vẫn nằm trong sổ sự kiện.

```bash
git switch research/p7-budget-feedback-20261104

# B luôn trả lại; so sánh cả ba cách xử lý mất thông báo.
python examples/two_agents.py

# B giữ tài nguyên; chỉ in kết quả tổng hợp.
python examples/two_agents.py --scenario hostile --summary-only

# B giữ tài nguyên 10 lượt đầu rồi bắt đầu hợp tác.
python examples/two_agents.py --scenario recovery --summary-only

# Chỉ chạy A có đối chiếu biên nhận, đồng thời lưu sổ sự kiện và diễn biến.
python examples/two_agents.py --mode reconcile --out two-agents.json
```

Với cấu hình mặc định, A chỉ chờ thông báo gửi được **8 lần**, còn A đối chiếu biên nhận gửi đủ **20 lần**, khi B luôn trả tài nguyên. Khi B luôn giữ tài nguyên, hai cách an toàn dừng ở mức mất **4 đơn vị**; cách tự mở khóa theo thời gian mất **6 đơn vị**.

Đây là hai agent có chính sách viết bằng mã, chạy trên CPU và không gọi mô hình ngôn ngữ. Xem [thiết kế và cách chạy](docs/experiments/TWO-AGENT-RECEIPT-SIMULATION.md) hoặc chạy `python examples/two_agents.py --help` để xem tham số.

## Dự án đã có những gì?

| Thành phần | Phần đã triển khai để nghiên cứu | Mục tiêu dài hạn |
|---|---|---|
| HyperMemory | Lưu sự kiện chính xác, bộ dự đoán gọn, cập nhật theo dữ liệu mới và thí nghiệm SQLite | Bộ nhớ phù hợp với từng nhiệm vụ, đo được chất lượng và chi phí |
| MathKernel | Các mô hình chuyển trạng thái ngẫu nhiên hữu hạn, cập nhật xác suất và biểu diễn quần thể | Mô hình toán học có thể kiểm chứng cho quyết định của agent |
| World Runtime | Tương tác trên đồ thị thưa, chuyển tài nguyên, phát lại xác định và lưu mốc trạng thái | Môi trường tồn tại lâu dài với cơ chế điều phối đáng tin cậy |
| Quyền truy cập và giao thức | Các bản triển khai tham chiếu về quyền có phạm vi, thu hồi quyền, giao dịch và khôi phục | Danh tính, sự đồng ý và khả năng liên thông được thẩm định |
| Đánh giá | Chuỗi nghiên cứu học và hợp tác P1–P7; bộ đo W5 về lưu trữ, bộ nhớ và phục hồi | Bằng chứng có thể tái lập trước khi mở rộng dự án |

**SuperKernel** là kiến trúc tổng thể để quản lý vòng đời agent, chính sách hành động, công cụ, ngân sách và lịch thực thi. Bộ nhân hoàn chỉnh cho vận hành thực tế, hệ thống phục vụ mô hình dùng chung, xã hội agent tự vận hành và mạng thế giới liên thông vẫn là mục tiêu tương lai. Xem [kiến trúc](docs/ARCHITECTURE.md) và [lộ trình](docs/ROADMAP.md).

## Nghiên cứu mới nhất: kiểm tra bằng chứng trước khi mở lại hạn mức

Hãy hình dung agent A gửi một đơn vị tài nguyên cho B. B đã trả lại, nhưng thông báo cho A bị mất. A vẫn coi lần chuyển đó là chưa được xác nhận, tiếp tục giữ một phần hạn mức rủi ro và cuối cùng có thể ngừng hợp tác dù B vẫn trả đầy đủ.

**P7 kiểm tra xem đối chiếu biên nhận trả lại đã được ghi nhận chính xác có giúp agent tiếp tục hợp tác hay không.** Thí nghiệm so sánh ba cách: chỉ chờ thông báo, định kỳ kiểm tra biên nhận và tự giải phóng hạn mức sau thời gian chờ. Cách cuối được đưa vào làm đối chứng không an toàn: chờ đủ lâu không chứng minh rằng tài nguyên đã được trả lại.

[Báo cáo đo ngày 04/11/2026](docs/evaluation/P7-HOLDOUT-RESULTS-20261104.md) ghi lại **960 trường hợp trên 10 seed mới**. Seed là giá trị khởi tạo giúp tái lập một thế giới mô phỏng. Ma trận thử nghiệm gồm bốn chính sách hành động, bốn kiểu đối tác, hai kênh phản hồi và ba cách xử lý biên nhận.

| Phát hiện | Kết quả đo được |
|---|---|
| Đối tác hợp tác nhưng thông báo chậm hoặc bị mất | Đối chiếu biên nhận nâng điểm thưởng trung bình mỗi quyết định của bên gửi từ **0,5421 lên 0,6000** |
| Chỉ chờ thông báo hoặc đối chiếu biên nhận chính xác | **640/640 trường hợp** giữ đúng giới hạn rủi ro bốn đơn vị cho mỗi bên gửi |
| Tự giải phóng hạn mức khi hết thời gian chờ | **90/320 trường hợp** vượt giới hạn rủi ro thực tế, cao nhất tám đơn vị |
| Ngân sách đã bị tiêu hết bởi tổn thất được xác nhận | Đối chiếu biên nhận không khôi phục được ngân sách đó |
| Đối tác lúc hợp tác, lúc từ chối | Thưởng trung bình tăng, nhưng mỗi chính sách có chuyển tài nguyên vẫn bị giảm thưởng ở **3/10 seed** |

Đây là điểm thưởng được thiết kế cho mô phỏng một chủ sở hữu. Các lần chuyển tài nguyên W3 hoàn tất ngay; chỉ thông báo bị chậm hoặc mất. Kết quả xác nhận lợi ích của việc đối chiếu bằng chứng trong phạm vi thí nghiệm này, chưa chứng minh một chính sách hợp tác tốt cho mọi tình huống hay mức an toàn khi vận hành thực tế.

Chạy lại nghiên cứu P7 trên nhánh hiện tại:

```bash
# P7 hiện được công bố trên nhánh nghiên cứu này.
git switch research/p7-budget-feedback-20261104

python -m unittest discover -s tests -p test_p7_receipt_reconciliation.py -v
python benchmarks/p7_receipt_reconciliation.py --split development --out p7-development.json
python benchmarks/p7_receipt_reconciliation.py --split holdout --out p7-holdout.json
```

Xem [thiết kế đã cố định trước khi thử nghiệm](docs/evaluation/P7-RECEIPT-RECONCILIATION-PROTOCOL.md), [toàn bộ dữ liệu kiểm tra bằng seed mới](research/runs/2026-11-04/p7-holdout.json) và [hồ sơ kiểm chứng](research/runs/2026-11-04/validation.json). Báo cáo chỉ rõ commit mã nguồn được dùng để đo; các commit cập nhật tài liệu sau đó được ghi riêng.

## Tiến trình nghiên cứu

Mỗi nghiên cứu trả lời một câu hỏi có phạm vi cụ thể. Kết quả mô phỏng không chứng minh trí thông minh trong thế giới thực, sự xuất hiện của xã hội agent hay khả năng triển khai ở quy mô lớn.

| Nghiên cứu | Câu hỏi và bằng chứng |
|---|---|
| W5 — biểu diễn quần thể | Giá trị trung bình, biểu đồ tần suất hay bản tóm tắt phân phối giữ được thông tin hữu ích đến đâu? [Nghiên cứu cơ sở](docs/evaluation/W5-POPULATION-REPRESENTATION-BASELINES.md) |
| P1 | Ba mươi agent mô phỏng có thể học từ phần thưởng của hành động đã chọn không? [Nghiên cứu](docs/evaluation/P1-THIRTY-AGENT-ONLINE-LEARNING.md) |
| P2 | Hợp tác có trạng thái thay đổi việc học trong thế giới có thể phát lại như thế nào? [Nghiên cứu](docs/evaluation/P2-STATEFUL-COOPERATION-EXPERIMENT.md) |
| P3 | Điều gì xảy ra khi bên gửi và bên nhận học chính sách riêng? [Nghiên cứu](docs/evaluation/P3-MUTUAL-LEARNING-W3.md) |
| P4 | Cách biểu diễn nào giúp học từ ít mẫu hơn khi đối tác thay đổi? [Kết quả](docs/evaluation/P4-FIVE-SEED-RESULTS-REPORT.md) |
| P5 | Không hành động và thăm dò có lợi ích, tổn thất như thế nào? [Kết quả](docs/evaluation/P5-FIVE-SEED-RESULTS-REPORT.md) |
| P6 | Giới hạn rủi ro cứng hoạt động ra sao khi phản hồi bị thiếu? [Kết quả 840 trường hợp](docs/evaluation/P6-TEN-SEED-RESULTS-REPORT.md) |
| P7 | Biên nhận chính xác có giảm tình trạng khóa hạn mức do mất thông báo không? [Kết quả 960 trường hợp](docs/evaluation/P7-HOLDOUT-RESULTS-20261104.md) |

[Bản đồ tài liệu nghiên cứu gốc](docs/research/RELATED-RESEARCH-AND-PROJECTS.md) liên kết các công trình trước với câu hỏi có thể kiểm chứng trong OpenWorld. Các đề xuất khác gồm [biểu diễn quần thể và bộ gen agent](docs/research/POPULATION-REPRESENTATION-AND-AGENT-DNA.md), [ghép các thành phần thế giới](docs/experiments/COMPOSABLE-WORLD-FIXTURE.md) và [nền tảng toán học](docs/math/RFC-007-OPENWORLD-MATHEMATICAL-FOUNDATIONS.md). Phạm vi đề xuất được phân biệt với phần đã triển khai và đo đạc.

## Kiểm chứng và giới hạn hiện tại

Đợt kiểm chứng trên **Windows ngày 04/11/2026** đã chạy **462 bài kiểm tra, không có lỗi ngoài dự kiến**, với sáu bài được bỏ qua và hai lỗi bảo mật đã biết được giữ làm đối chứng. Môi trường sử dụng Python 3.14.7 và SQLite 3.53.4. Chi tiết nằm trong [nhật ký đầy đủ](research/runs/2026-11-04/final-tests.log) và [báo cáo đo](docs/evaluation/P7-HOLDOUT-RESULTS-20261104.md).

- Hai lỗi đã biết liên quan đến quyền truy cập và tính nguyên tử: phục hồi bản sao lưu quyền cũ có thể làm quyền đã thu hồi hoạt động trở lại; việc sử dụng quyền và tác động tiếp theo lên thế giới chưa được gộp thành một giao dịch duy nhất cùng thành công hoặc cùng thất bại.
- Một bài kiểm tra PostgreSQL thực và năm bài kiểm tra trình chạy Bash đã được bỏ qua. Đợt kiểm chứng này chưa xác nhận PostgreSQL thực hoạt động tương đương SQLite.
- Bằng chứng lịch sử chính xác được tách khỏi dự đoán và phát lại mô phỏng. Nội dung được sinh ra không chứng minh rằng một sự kiện ngoài đời đã xảy ra.
- Truy cập dữ liệu của chủ sở hữu khác và hành động tác động ra bên ngoài cần được cho phép rõ ràng. Các ví dụ cùng một chủ sở hữu chưa chứng minh được sự đồng ý độc lập của hai bên.
- Số lượng agent được đăng ký không đo được số lượt suy luận mô hình đồng thời. Dự án chưa chứng minh năng lực hàng tỷ agent, nén bộ nhớ cho mọi loại dữ liệu hay trí thông minh tổng quát.
- Các bản lưu thử nghiệm cũ chưa được đưa vào kho mã, chờ rà soát quyền sử dụng, bí mật, bảo mật và khả năng tái lập.

## Hướng nghiên cứu tiếp theo

1. Lưu bền vững ngân sách và biên nhận; kiểm tra khởi động lại, thông báo trùng và lỗi xảy ra giữa lúc chấp nhận chuyển tài nguyên với lúc ghi khoản giữ hạn mức.
2. So sánh cách giữ lại một phần hạn mức để thăm dò muộn, trong cùng giới hạn tổng và khi chưa biết lúc nào đối tác sẽ hợp tác trở lại.
3. Đo lợi ích của bộ nhớ đối với quyết định, đồng thời đo khả năng truy xuất lịch sử chính xác, CPU, dung lượng đĩa và chi phí nhật ký SQLite WAL.
4. Đánh giá các đối tác mới có khả năng thích nghi trước khi mở rộng sang thế giới phân tán hoặc liên thông.

Đây là các nghiên cứu được đề xuất. Thay đổi phần thực thi dùng chung cần được rà soát kiến trúc và khả năng tương thích. Xem [tổng hợp trạng thái hiện tại](docs/project/RESEARCH-SNAPSHOT-20261104.md) và [trạng thái nghiên cứu](research/RESEARCH-STATUS.md).

## Cấu trúc kho mã

- [`src/openworld_superkernel/`](src/openworld_superkernel/): các bản triển khai tham chiếu.
- [`benchmarks/`](benchmarks/): thí nghiệm mô phỏng có thể chạy lại.
- [`tests/`](tests/): kiểm tra tính bất biến, tình huống lỗi và tích hợp.
- [`examples/`](examples/): ví dụ chạy trên máy cục bộ.
- [`docs/`](docs/): kiến trúc, giao thức, quyết định và báo cáo thí nghiệm.
- [`research/`](research/): trạng thái nghiên cứu và bằng chứng từ các lần chạy.

Đây là kho [iamphan04/OpenWorld](https://github.com/iamphan04/OpenWorld), được tách nhánh từ [CocAgent/OpenWorld](https://github.com/CocAgent/OpenWorld). Các liên kết issue và pull request cũ trỏ về lịch sử của kho gốc. Khi tiếp tục công việc, đọc [trạng thái mới nhất](docs/project/RESEARCH-SNAPSHOT-20261104.md), [bối cảnh dự án](docs/project/PROJECT-CONTINUITY.md), [sổ quyết định](docs/project/DECISION-LEDGER.md), [sổ nguồn tài liệu](docs/project/SESSION-SOURCE-REGISTER.md) và [tài liệu bàn giao](docs/project/EXECUTION-HANDOFF.md).

## Đóng góp và giấy phép

README này được viết bằng **tiếng Việt**. Mã nguồn, chú thích, tài liệu khác, issue và pull request tiếp tục sử dụng tiếng Anh theo quy ước đóng góp hiện tại. Đóng góp nghiên cứu cần nêu giả định, phương pháp đối chiếu, seed, kết quả bất lợi, cách kiểm chứng cục bộ và cách hoàn tác. Xem [hướng dẫn đóng góp](CONTRIBUTING.md), [các nhóm công việc](docs/WORKSTREAMS.md) và [bảo mật](SECURITY.md).

Mã nguồn và tài liệu mới do OpenWorld tạo ra được cấp phép theo [Apache-2.0](LICENSE). Các dự án bên thứ ba được dẫn chiếu và tài liệu lịch sử giữ nguyên quyền và yêu cầu rà soát tương ứng.
