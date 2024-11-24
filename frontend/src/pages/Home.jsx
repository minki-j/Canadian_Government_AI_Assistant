import { useState, useEffect } from "react";

const Home = () => {
  const [aiMessages, setAiMessages] = useState([]);
  const [userInput, setUserInput] = useState("");
  const [websiteContent, setWebsiteContent] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [showBanner, setShowBanner] = useState(true);

  useEffect(() => {
    const fetchWebsite = async () => {
      try {
        const response = await fetch('/fetch_website_content', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            url: 'https://www.canada.ca/en/services/benefits.html'
          })
        });
        
        if (!response.ok) throw new Error('Failed to fetch website');
        
        const html = await response.text();
        setWebsiteContent(html);
      } catch (error) {
        console.error('Error fetching website:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchWebsite();
  }, []);

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!userInput.trim()) return;

    // Add user message to chat
    setAiMessages(prev => [...prev, { type: 'user', content: userInput }]);
    
    // TODO: Implement AI response logic here
    // For now, just mock a response
    setTimeout(() => {
      setAiMessages(prev => [...prev, { 
        type: 'ai', 
        content: "I can help you navigate the website. What would you like to know?"
      }]);
    }, 1000);

    setUserInput("");
  };

  return (
    <div className="flex">
      {/* Left Panel - Chat Interface */}
      <div className="w-1/2 border-r border-gray-200 flex flex-col">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {aiMessages.map((message, index) => (
            <div
              key={index}
              className={`p-3 rounded-lg ${
                message.type === "user" ? "bg-blue-100 ml-auto" : "bg-gray-100"
              } max-w-[80%]`}
            >
              {message.content}
            </div>
          ))}
        </div>
        <form
          onSubmit={handleSendMessage}
          className="p-4 border-t border-gray-200"
        >
          <div className="flex gap-2">
            <input
              type="text"
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              placeholder="Ask me anything..."
              className="flex-1 p-2 border border-gray-300 rounded"
            />
            <button
              type="submit"
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Send
            </button>
          </div>
        </form>
      </div>

      {/* Right Panel - Website View */}
      <div className="w-1/2 overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center relative h-[calc(100vh-85px)]">
            <div className="text-m text-gray-600">Loading website...</div>
          </div>
        ) : (
          <div className="relative h-[calc(100vh-60px)]">
            <div className="w-full h-full overflow-y-auto overflow-x-hidden website-container pt-6 opacity-85">
              <div className="absolute top-0 left-0 right-0 bg-gray-800 text-white text-m py-1 px-2 text-center z-10 opacity-90">
                This is a preview of what the AI can see, not a real website.
              </div>
              <div
                className="pointer-events-none"
                dangerouslySetInnerHTML={{ __html: websiteContent }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Home;
