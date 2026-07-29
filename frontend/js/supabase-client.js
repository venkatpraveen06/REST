// Supabase Client Helper for Realtime Subscriptions
const SUPABASE_URL = "https://beyifxgwklaloleuxhzk.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJleWlmeGd3a2xhbG9sZXV4aHprIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODUzMDc2NTAsImV4cCI6MjEwMDg4MzY1MH0.N0ibgMRCbBRO75zsC8Q5_-CS8Fu2wqMu3WO_MU-oaAs";

const supabaseClient = (typeof window !== 'undefined' && window.supabase) 
    ? window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY) 
    : null;

class AuraSupabaseRealtime {
    static subscribeToLiveOrders(restaurantId, onNewOrderCallback) {
        if (!supabaseClient) {
            console.warn("Supabase JS SDK not loaded yet.");
            return null;
        }

        console.log(`Subscribed to Realtime orders for restaurant: ${restaurantId}`);
        return supabaseClient
            .channel('public:orders')
            .on('postgres_changes', {
                event: 'INSERT',
                schema: 'public',
                table: 'orders',
                filter: `restaurant_id=eq.${restaurantId}`
            }, (payload) => {
                console.log("Realtime New Order Received:", payload.new);
                onNewOrderCallback(payload.new);
            })
            .subscribe();
    }
}

window.AuraSupabaseRealtime = AuraSupabaseRealtime;
