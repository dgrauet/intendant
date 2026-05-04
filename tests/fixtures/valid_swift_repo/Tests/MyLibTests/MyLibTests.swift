import XCTest
@testable import MyLib

final class MyLibTests: XCTestCase {
    func testAdd() {
        XCTAssertEqual(MyLib().add(2, 3), 5)
    }
}
