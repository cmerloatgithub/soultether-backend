import SwiftUI

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

#Preview {
    OpeningScreenView(viewModel: AppViewModel())
}
