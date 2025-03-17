import {create} from 'zustand';
import { persist } from 'zustand/middleware';
import axios from 'axios';
import Cookies from 'js-cookie';

interface File {
    id: number,
    data: any,
}

interface FileStore {
    file: File,
    uploadFile: (file: any) =>Promise<void>,
    deleteFile: (file: any) => void,
    getFile:()=>void,
    getMatches:()=>Promise<void>,
    getInfo:()=>Promise<void>,
}

const useFileStore = create<FileStore>()(
    (set, get) => ({
        file: { id: 0, data: null },
        uploadFile: async (file: any) => {
            const formData = new FormData();
            formData.append('file', file.data);
            axios.post('/api/upload', formData, {
                headers: {
                    'Content-Type':'multipart/form-data',
                    'Authorization': `Bearer ${Cookies.get('access_token')}`
                }
            }).then(response => {
                set({ ...file,id: response.data.resume_id });
            }).catch(error => {
                console.log(error);
            });
        },
        getMatches: async ()=> {

        },
        getInfo: async ()=> {

        },
        deleteFile: (file: any) => {
            axios.delete('/api/delete/' + file.id, {
                headers: {
                    'Authorization': `Bearer ${Cookies.get('access_token')}`
                }
            }).catch(error => {
                console.log(error);
            });
        },
        getFile:()=> {
            axios.get('/api/files', {
                headers: {
                    'Authorization': `Bearer ${Cookies.get('access_token')}`
                }
            }).then(response => {
                set({ file: response.data });
            }).catch(error => {
                console.log(error);
            });
        }
    })
)

export default useFileStore;