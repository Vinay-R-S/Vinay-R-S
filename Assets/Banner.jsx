export default function Banner() {
    return (
        <div className="min-h-screen bg-black flex items-center justify-center p-8">
            <div className="w-full max-w-6xl">

                {/* Banner Container */}
                <div className="relative w-full aspect-[4/1] max-w-[1600px] mx-auto">
                    <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-blue-500/20 via-purple-500/15 to-green-500/20" />
                    <div className="absolute inset-0 rounded-2xl bg-gradient-to-tl from-green-400/15 via-blue-400/10 to-purple-400/15" />

                    <div className="absolute inset-0 rounded-2xl overflow-hidden">
                        <div className="absolute inset-0 rounded-2xl border-gradient-animated" />
                    </div>

                    <div className="relative h-full bg-black/50 backdrop-blur-16xl rounded-2xl overflow-hidden border border-white/20">
                        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 via-purple-500/8 to-green-500/10" />
                        <div className="absolute inset-0 bg-gradient-to-tl from-green-400/8 via-transparent to-blue-400/8" />
                        <div className="absolute inset-0 backdrop-blur-4xl bg-black/30" />

                        {/* Content */}
                        <div className="relative h-full flex items-center justify-center px-12 z-10">
                            <div className="text-center space-y-4">
                                {/* Hello World Code */}
                                <div className="font-mono text-white text-xl md:text-2xl font-medium">{"<Hello World/>"}</div>

                                {/* Name */}
                                <h1 className="text-4xl md:text-6xl font-bold text-white tracking-tight">I am, Vinay Saunshi</h1>

                            </div>
                        </div>

                        {/* <div className="absolute top-4 right-4 w-3 h-3 rounded-full bg-blue-400/60 blur-sm" />
            <div className="absolute bottom-4 left-4 w-2 h-2 rounded-full bg-purple-400/50 blur-sm" /> */}
                    </div>
                </div>

            </div>
        </div>
    )
}