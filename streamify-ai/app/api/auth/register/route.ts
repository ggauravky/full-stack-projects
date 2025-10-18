import { connectToDatabase } from "@/lib/db";
import User from  from "@/models/user";
import { NextRequest,NextResponse } from "next/server";
import { error } from "console";

export async function POST(req:NextRequest){
    try{
        const {email,name,password}=await req.json();

        if(!email || !name || !password){
            return NextResponse.json(error("Missing required fields"),{status:400})
        }

        await connectToDatabase();

        const existingUser=await User.findOne({email})
        if(existingUser){
            return NextResponse.json(error("User already exists"),{status:400});
        }

        await User.create({email,name,password})

        return NextResponse.json({message:"User registered successfully"},{status:201});

    } catch(error){
        console.error("Error registering user:",error);
        return NextResponse.json({error:"Internal Server Error"},{status:500});
    }
}