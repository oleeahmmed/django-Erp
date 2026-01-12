import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { Building2, Moon, Sun } from "lucide-react"
import { login } from "@/lib/auth"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { toast } from "sonner"
import { useTheme } from "@/components/theme-provider"

export function Login() {
  const navigate = useNavigate()
  const { toggleTheme } = useTheme()
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!username || !password) {
      toast.error("Please enter username and password")
      return
    }

    setIsLoading(true)
    try {
      await login({ username, password })
      toast.success("Login successful!")
      navigate("/")
    } catch (error: any) {
      const message = error.response?.data?.detail || "Invalid credentials"
      toast.error(message)
    } finally {
      setIsLoading(false)
    }
  }

  // Theme toggle with animation coordinates
  const handleThemeToggle = (event: React.MouseEvent<HTMLButtonElement>) => {
    const { clientX: x, clientY: y } = event
    toggleTheme({ x, y })
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/50 p-4">
      {/* Theme Toggle Button - Top Right */}
      <Button
        variant="outline"
        size="icon"
        className="absolute top-4 right-4 border-none bg-transparent shadow-none"
        onClick={handleThemeToggle}
      >
        <Sun className="h-[1.25rem] w-[1.25rem] scale-150 rotate-0 fill-[#f99100] stroke-[#f99100] transition-all dark:scale-0 dark:-rotate-90" />
        <Moon className="absolute h-[1.25rem] w-[1.25rem] scale-0 rotate-90 fill-[#8eb1ff] stroke-[#8eb1ff] transition-all dark:scale-150 dark:rotate-0" />
        <span className="sr-only">Toggle Theme</span>
      </Button>

      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <Building2 className="h-6 w-6" />
            </div>
          </div>
          <CardTitle className="text-2xl">ERP System</CardTitle>
          <CardDescription>Enter your credentials to login</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                type="text"
                placeholder="Enter username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={isLoading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading}
              />
            </div>
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "Logging in..." : "Login"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
