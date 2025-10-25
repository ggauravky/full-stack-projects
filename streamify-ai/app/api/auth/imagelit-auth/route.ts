import { getUploadAuthParams } from "@imagekit/next/server"

export async function GET() {

    try {
        const authenticationParameters = getUploadAuthParams({
        privateKey: process.env.IMAGEKIT_PRIVATE_KEY as string, 
        publicKey: process.env.IMAGEKIT_PUBLIC_KEY as string,
    })

    return Response.json({authenticationParameters, publicKey: process.env.NEXT_PUBLIC_IMAGEKIT_PUBLIC_KEY});
    } catch (error) {
        return Response.json({error: 'Failed to get authentication parameters'}, {status: 500});
    }

    
}