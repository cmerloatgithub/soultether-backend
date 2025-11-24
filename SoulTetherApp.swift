import SwiftUI

@main
struct SoulTetherApp: App {
    @StateObject private var viewModel = AppViewModel()
    
    var body: some Scene {
        WindowGroup {
            ZStack {
                Color(red: 0.95, green: 0.95, blue: 0.95)
                    .ignoresSafeArea()
                
                switch viewModel.currentScreen {
                case .opening:
                    OpeningScreenView(viewModel: viewModel)
                case .birthData:
                    BirthDataScreenView(viewModel: viewModel)
                case .reader:
                    ReaderScreenView(viewModel: viewModel)
                }
            }
        }
    }
}

enum Screen {
    case opening
    case birthData
    case reader
}

@MainActor
class AppViewModel: ObservableObject {
    @Published var currentScreen: Screen = .opening
    @Published var reading: String = ""
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    @Published var chartData: ChartData?
    
    private let baseURL = "https://web-production-93b91.up.railway.app"
    
    func navigateTo(_ screen: Screen) {
        self.currentScreen = screen
    }
    
    func calculateReading(
        birthDate: String,
        hour: Int,
        minute: Int,
        isAM: Bool,
        location: String
    ) async {
        isLoading = true
        errorMessage = nil
        
        do {
            let url = URL(string: "\(baseURL)/calculate_reading")!
            var request = URLRequest(url: url)
            request.httpMethod = "POST"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            
            let payload: [String: Any] = [
                "birth_date": birthDate,
                "hour": hour,
                "minute": minute,
                "is_am": isAM,
                "location": location
            ]
            
            request.httpBody = try JSONSerialization.data(withJSONObject: payload)
            
            let (data, response) = try await URLSession.shared.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse,
                  (200...299).contains(httpResponse.statusCode) else {
                throw NSError(domain: "HTTP", code: -1, userInfo: [NSLocalizedDescriptionKey: "Invalid response"])
            }
            
            let decoder = JSONDecoder()
            let result = try decoder.decode(ReadingResponse.self, from: data)
            
            if result.success {
                self.reading = result.reading
                self.chartData = result.chart_data
                self.currentScreen = .reader
            } else {
                self.errorMessage = result.error ?? "Unknown error"
            }
        } catch {
            self.errorMessage = "Failed to calculate reading: \(error.localizedDescription)"
        }
        
        isLoading = false
    }
}

struct ReadingResponse: Codable {
    let success: Bool
    let reading: String
    let error: String?
    let chart_data: ChartData?
    
    enum CodingKeys: String, CodingKey {
        case success, reading, error, chart_data = "chart_data"
    }
}

struct ChartData: Codable {
    let birth: String
    let location: String
    let coordinates: Coordinates
    let ascendant: String
    let midheaven: String
    let planets: [String: PlanetData]
    let fol_hits: Int
    
    enum CodingKeys: String, CodingKey {
        case birth, location, coordinates, ascendant, midheaven, planets
        case fol_hits = "fol_hits"
    }
}

struct Coordinates: Codable {
    let lat: Double
    let lon: Double
}

struct PlanetData: Codable {
    let lon: Double
    let sign: String
    let deg: Double
    let house: Int
}

struct OpeningScreenView: View {
    @ObservedObject var viewModel: AppViewModel
    
    var body: some View {
        ZStack {
            Color(red: 0.95, green: 0.95, blue: 0.95)
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                HStack {
                    Button(action: { }) {
                        Text("☰")
                            .font(.system(size: 24))
                            .foregroundColor(.black)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding()
                    
                    Spacer()
                }
                .frame(height: 50)
                
                Spacer()
                    .frame(height: 40)
                
                Image("SoulTetherOpen")
                    .resizable()
                    .scaledToFit()
                    .frame(maxHeight: 300)
                    .padding(.horizontal, 20)
                
                Spacer()
                    .frame(height: 60)
                
                Button(action: {
                    viewModel.navigateTo(.birthData)
                }) {
                    Text("")
                        .frame(maxWidth: .infinity)
                        .frame(height: 60)
                        .background(Color(red: 0.3, green: 0.8, blue: 1))
                        .cornerRadius(30)
                }
                .padding(.horizontal, 40)
                
                Text("Press When Ready")
                    .font(.system(size: 16, weight: .regular))
                    .foregroundColor(Color(red: 1, green: 0.2, blue: 0.2))
                    .padding(.top, 20)
                
                Spacer()
                    .frame(height: 40)
            }
        }
    }
}

struct BirthDataScreenView: View {
    @ObservedObject var viewModel: AppViewModel
    
    @State private var birthDate: String = ""
    @State private var hour: String = "12"
    @State private var minute: String = "00"
    @State private var isAM: Bool = true
    @State private var location: String = ""
    
    var body: some View {
        ZStack {
            Color(red: 0.95, green: 0.95, blue: 0.95)
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                HStack {
                    Button(action: { }) {
                        Text("☰")
                            .font(.system(size: 24))
                            .foregroundColor(.black)
                    }
                    .padding()
                    
                    Image("SoulTetherIcon")
                        .resizable()
                        .scaledToFit()
                        .frame(width: 40, height: 40)
                    
                    Spacer()
                }
                .frame(height: 50)
                
                ScrollView {
                    VStack(spacing: 20) {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("ENTER BIRTH DATE")
                                .font(.system(size: 14, weight: .semibold))
                                .foregroundColor(.black)
                            
                            TextField("YYYY-MM-DD", text: $birthDate)
                                .textFieldStyle(RoundedBorderTextFieldStyle())
                                .foregroundColor(.black)
                                .frame(height: 45)
                        }
                        
                        VStack(alignment: .leading, spacing: 8) {
                            Text("BIRTH TIME")
                                .font(.system(size: 14, weight: .semibold))
                                .foregroundColor(.black)
                            
                            HStack(spacing: 10) {
                                VStack(spacing: 5) {
                                    TextField("HH", text: $hour)
                                        .textFieldStyle(RoundedBorderTextFieldStyle())
                                        .keyboardType(.numberPad)
                                        .frame(height: 40)
                                    Text("Hour")
                                        .font(.caption)
                                        .foregroundColor(.gray)
                                }
                                
                                Text(":")
                                    .font(.system(size: 20, weight: .semibold))
                                
                                VStack(spacing: 5) {
                                    TextField("MM", text: $minute)
                                        .textFieldStyle(RoundedBorderTextFieldStyle())
                                        .keyboardType(.numberPad)
                                        .frame(height: 40)
                                    Text("Minute")
                                        .font(.caption)
                                        .foregroundColor(.gray)
                                }
                                
                                Spacer()
                                
                                VStack(spacing: 8) {
                                    Button(action: { isAM = true }) {
                                        Text("AM")
                                            .frame(maxWidth: .infinity)
                                            .frame(height: 35)
                                            .background(isAM ? Color(red: 0.9, green: 0.2, blue: 0.2) : Color(red: 0.3, green: 0.7, blue: 1))
                                            .foregroundColor(.white)
                                            .cornerRadius(8)
                                    }
                                    
                                    Button(action: { isAM = false }) {
                                        Text("PM")
                                            .frame(maxWidth: .infinity)
                                            .frame(height: 35)
                                            .background(isAM ? Color(red: 0.3, green: 0.7, blue: 1) : Color(red: 0.9, green: 0.2, blue: 0.2))
                                            .foregroundColor(.white)
                                            .cornerRadius(8)
                                    }
                                }
                            }
                        }
                        
                        VStack(alignment: .leading, spacing: 8) {
                            Text("BIRTH LOCATION")
                                .font(.system(size: 14, weight: .semibold))
                                .foregroundColor(.black)
                            
                            TextField("City, Country", text: $location)
                                .textFieldStyle(RoundedBorderTextFieldStyle())
                                .foregroundColor(.black)
                                .frame(height: 45)
                        }
                        
                        Spacer()
                            .frame(height: 20)
                    }
                    .padding(20)
                }
                
                if viewModel.isLoading {
                    ProgressView()
                        .frame(height: 60)
                }
                
                if let error = viewModel.errorMessage {
                    Text(error)
                        .font(.caption)
                        .foregroundColor(.red)
                        .padding()
                }
                
                Button(action: {
                    Task {
                        let hour = Int(hour) ?? 12
                        let minute = Int(minute) ?? 0
                        await viewModel.calculateReading(
                            birthDate: birthDate,
                            hour: hour,
                            minute: minute,
                            isAM: isAM,
                            location: location
                        )
                    }
                }) {
                    Text("")
                        .frame(maxWidth: .infinity)
                        .frame(height: 60)
                        .background(Color(red: 1, green: 0.7, blue: 0.2))
                        .cornerRadius(8)
                }
                .padding(15)
                .disabled(viewModel.isLoading)
                
                Text("Press When Ready")
                    .font(.system(size: 14))
                    .foregroundColor(Color(red: 0.3, green: 0.7, blue: 1))
                    .padding(.bottom, 15)
            }
        }
    }
}

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
