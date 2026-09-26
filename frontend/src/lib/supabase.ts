import { createClient } from "@supabase/supabase-js";

// Same Supabase project as the online course platform, so students sign in
// with their existing course account.
export const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
);

export const coursePlatformUrl = import.meta.env.VITE_COURSE_PLATFORM_URL || "";
