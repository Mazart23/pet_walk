import { Menu } from "@/types/menu";
import { FaHome, FaInfoCircle } from "react-icons/fa";

const menuData: Menu[] = [
  {
    id: 0,
    title: <FaHome size={26}/>,
    path: "/",
    newTab: false,
  },
  {
    id: 1,
    title: <FaInfoCircle size={26}/>,
    path: "/about",
    newTab: false,
  },
];
export default menuData;
