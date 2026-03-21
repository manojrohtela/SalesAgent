  import { createRoot } from "react-dom/client";
  import App from "./app/App.tsx";
  import "./styles/index.css";
  import { DataProvider } from "./app/DataContext";

  createRoot(document.getElementById("root")!).render(
    <DataProvider>
      <App />
    </DataProvider>
  );