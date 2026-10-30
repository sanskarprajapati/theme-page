// Subject cut-out with Apple Vision (VNGenerateForegroundInstanceMaskRequest, macOS 14+).
// Usage: cutout <in.jpg|png> <out.png> [--all]      one image
//        cutout <frames_dir> <out_dir> [--all]      every .png in the folder, same file names
// Writes RGBA PNGs at the source size, background transparent. Keeps only the largest subject
// (the hero, not bystanders) unless --all is passed.
import AppKit
import CoreImage
import Vision

let ctx = CIContext()
let srgb = CGColorSpace(name: CGColorSpace.sRGB)!

func largestInstance(_ obs: VNInstanceMaskObservation) -> IndexSet {
    let mask = obs.instanceMask
    CVPixelBufferLockBaseAddress(mask, .readOnly)
    defer { CVPixelBufferUnlockBaseAddress(mask, .readOnly) }
    let width = CVPixelBufferGetWidth(mask), height = CVPixelBufferGetHeight(mask)
    let stride = CVPixelBufferGetBytesPerRow(mask)
    let base = CVPixelBufferGetBaseAddress(mask)!.assumingMemoryBound(to: UInt8.self)
    var counts = [Int](repeating: 0, count: 256)
    for y in 0..<height {
        for x in 0..<width { counts[Int(base[y * stride + x])] += 1 }
    }
    let best = obs.allInstances.max { counts[$0] < counts[$1] } ?? 1
    return IndexSet(integer: best)
}

func cut(_ src: URL, _ dst: URL, all: Bool) throws {
    let handler = VNImageRequestHandler(url: src)
    let request = VNGenerateForegroundInstanceMaskRequest()
    try handler.perform([request])
    guard let obs = request.results?.first else {
        throw NSError(domain: "cutout", code: 1,
                      userInfo: [NSLocalizedDescriptionKey: "no foreground subject found in \(src.lastPathComponent)"])
    }
    let keep = all ? obs.allInstances : largestInstance(obs)
    let buffer = try obs.generateMaskedImage(ofInstances: keep, from: handler, croppedToInstancesExtent: false)
    try ctx.writePNGRepresentation(of: CIImage(cvPixelBuffer: buffer), to: dst, format: .RGBA8, colorSpace: srgb)
}

let args = CommandLine.arguments
let keepAll = args.contains("--all")
guard args.count == (keepAll ? 4 : 3) else {
    FileHandle.standardError.write("usage: cutout <in> <out> [--all]\n".data(using: .utf8)!)
    exit(2)
}
let src = URL(fileURLWithPath: args[1]), dst = URL(fileURLWithPath: args[2])
var isDir: ObjCBool = false
FileManager.default.fileExists(atPath: src.path, isDirectory: &isDir)
do {
    if isDir.boolValue {
        try FileManager.default.createDirectory(at: dst, withIntermediateDirectories: true)
        let frames = try FileManager.default.contentsOfDirectory(atPath: src.path).filter { $0.hasSuffix(".png") }.sorted()
        for name in frames {
            try cut(src.appendingPathComponent(name), dst.appendingPathComponent(name), all: keepAll)
        }
    } else {
        try cut(src, dst, all: keepAll)
    }
} catch {
    FileHandle.standardError.write("cutout: \(error.localizedDescription)\n".data(using: .utf8)!)
    exit(1)
}
