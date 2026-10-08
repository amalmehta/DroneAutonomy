// Render the first page of a PDF to a PNG at a given scale (macOS PDFKit; no extra installs).
// Usage: swift scripts/pdf_to_png.swift in.pdf out.png [scale]
import PDFKit
import AppKit
let a = CommandLine.arguments
let doc = PDFDocument(url: URL(fileURLWithPath: a[1]))!
let page = doc.page(at: 0)!
let b = page.bounds(for: .mediaBox)
let s: CGFloat = a.count > 3 ? CGFloat(Double(a[3])!) : 3
let img = NSImage(size: NSSize(width: b.width * s, height: b.height * s))
img.lockFocus()
NSColor.white.set(); NSRect(x: 0, y: 0, width: b.width * s, height: b.height * s).fill()
let ctx = NSGraphicsContext.current!.cgContext
ctx.scaleBy(x: s, y: s)
page.draw(with: .mediaBox, to: ctx)
img.unlockFocus()
let rep = NSBitmapImageRep(data: img.tiffRepresentation!)!
try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: a[2]))
