// src/App.tsx
import { ThemeProvider } from "./contexts/ThemeContext";
import { BrowserRouter } from "react-router-dom";
import AppRouter from "./router/AppRouter";
import { Provider } from "react-redux";
import { store } from "./store/store"; 

function App() {
  return (
    <Provider store={store}> 
      <ThemeProvider>
        <div className="App">
          <BrowserRouter>
            <AppRouter />
          </BrowserRouter>
        </div>
      </ThemeProvider>
    </Provider>
  );
}

export default App;