import SwiftUI

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
                                .background(Color(red: 0.9, green: 0.2, blue: 0.2))
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
                                .background(Color(red: 0.9, green: 0.2, blue: 0.2))
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

#Preview {
    BirthDataScreenView(viewModel: AppViewModel())
}
