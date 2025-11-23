import SwiftUI

struct ReaderScreenView: View {
    @ObservedObject var viewModel: AppViewModel
    @State private var fontSize: CGFloat = 12
    
    var body: some View {
        ZStack {
            Color(red: 0.2, green: 0.5, blue: 0.6)
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                HStack(spacing: 15) {
                    Button(action: { }) {
                        Text("☰")
                            .font(.system(size: 24))
                            .foregroundColor(.white)
                    }
                    
                    Image("SoulTetherWhiteIcon")
                        .resizable()
                        .scaledToFit()
                        .frame(width: 30, height: 30)
                    
                    Spacer()
                }
                .padding(10)
                .frame(height: 50)
                .background(Color(red: 0.2, green: 0.5, blue: 0.6))
                
                ScrollView {
                    Text(viewModel.reading)
                        .font(.system(size: fontSize, design: .monospaced))
                        .foregroundColor(.black)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(15)
                        .background(Color.white)
                        .cornerRadius(8)
                        .padding(15)
                }
                .frame(maxHeight: .infinity)
                
                HStack(spacing: 10) {
                    Button(action: {
                        viewModel.navigateTo(.birthData)
                    }) {
                        Text("<")
                            .font(.system(size: 18))
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .frame(height: 50)
                    }
                    .frame(maxWidth: 60)
                    
                    HStack(spacing: 10) {
                        Button(action: {
                            fontSize = max(10, fontSize - 1)
                        }) {
                            Text("A")
                                .font(.system(size: 12))
                                .foregroundColor(.white)
                        }
                        
                        Text("•")
                            .foregroundColor(.white)
                        
                        Button(action: {
                            fontSize = min(18, fontSize + 1)
                        }) {
                            Text("A")
                                .font(.system(size: 14))
                                .foregroundColor(.white)
                        }
                    }
                    .frame(maxWidth: .infinity)
                    
                    Button(action: {
                        saveReading()
                    }) {
                        Text("↓")
                            .font(.system(size: 18))
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .frame(height: 50)
                    }
                    .frame(maxWidth: 60)
                }
                .padding(10)
                .background(Color(red: 0.2, green: 0.5, blue: 0.6))
                .frame(height: 50)
            }
        }
    }
    
    private func saveReading() {
        let fileName = "soultether_reading.txt"
        if let documentDirectory = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first {
            let fileURL = documentDirectory.appendingPathComponent(fileName)
            do {
                try viewModel.reading.write(to: fileURL, atomically: true, encoding: .utf8)
                showAlert(message: "Reading saved to Documents")
            } catch {
                showAlert(message: "Failed to save reading: \(error.localizedDescription)")
            }
        }
    }
    
    private func showAlert(message: String) {
        if let scene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
           let window = scene.windows.first,
           let rootViewController = window.rootViewController {
            let alert = UIAlertController(title: "Saved", message: message, preferredStyle: .alert)
            alert.addAction(UIAlertAction(title: "OK", style: .default))
            rootViewController.present(alert, animated: true)
        }
    }
}

#Preview {
    ReaderScreenView(viewModel: AppViewModel())
}
