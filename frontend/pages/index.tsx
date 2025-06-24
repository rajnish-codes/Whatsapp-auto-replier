import { useEffect, useState } from "react";
import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

type Message = {
  id: string;
  user_msg: "user" | "assistant";
  ai_reply: string;
  created_at: string;
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);

  useEffect(() => {
    const loadMessages = async () => {
      const { data } = await supabase
        .from("messages")
        .select("*")
        .order("created_at", { ascending: true });
      setMessages(data || []);
    };
    loadMessages();
  }, []);

  return (
    <div className="max-w-md mx-auto p-4 space-y-2">
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`p-3 rounded-xl max-w-xs ${
            msg.user_msg === "user"
              ? "bg-blue-500 text-white self-end ml-auto"
              : "bg-gray-200 text-black"
          }`}
        >
          <p>{msg.ai_reply}</p>
        </div>
      ))}
    </div>
  );
}
