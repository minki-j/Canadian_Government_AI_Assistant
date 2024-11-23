import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const Home = () => {
  const [isHealthy, setIsHealthy] = useState(false);

  useEffect(() => {
    console.log("Checking health...");
    const checkHealth = async () => {
      try {
        const response = await fetch("/health");
        if (response.ok) {
          const data = await response.json();
          console.log("Health check successful", data);
          setIsHealthy(true);
        }
      } catch (error) {
        console.error("Health check failed", error);
      }
    };

    checkHealth();
  }, []);

  return <div>{isHealthy ? "Healthy" : "Unhealthy"}</div>;
};

export default Home;
