import Foundation
import Vision
import AppKit
let dir = CommandLine.arguments[1]
let names = try FileManager.default.contentsOfDirectory(atPath: dir).filter{$0.hasSuffix(".jpg")}.sorted()
var out:[[String:Double]] = []
for (i,n) in names.enumerated() {
  let url = URL(fileURLWithPath: dir+"/"+n)
  let req = VNDetectFaceRectanglesRequest()
  let h = VNImageRequestHandler(url: url, options: [:])
  try? h.perform([req])
  let t = Double(i)/2.0
  if let r = (req.results ?? []).max(by: {$0.boundingBox.width<$1.boundingBox.width}) {
    let b = r.boundingBox
    out.append(["t":t,"x":b.midX,"y":1-b.midY,"w":b.width,"h":b.height])
  } else { out.append(["t":t,"x":-1,"y":-1,"w":0,"h":0]) }
}
let d = try JSONSerialization.data(withJSONObject: out)
FileManager.default.createFile(atPath: CommandLine.arguments[2], contents: d)
print(out.count)
