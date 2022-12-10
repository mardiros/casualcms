import React from "react";
import { Box, Flex } from "@chakra-ui/react";
import { useLocation } from "react-router-dom";
import { Header } from "./header";
import { SideBar } from "./sidebar";

type LayoutProps = {
  routes: React.ReactNode;
};

export const Layout: React.FunctionComponent<LayoutProps> = (props: LayoutProps) => {
  const location = useLocation();
  if (location.pathname.startsWith("/admin/pages/preview")) {
    return <></>;
  }
  return (
    <>
      <Box w="100%" p={4} bg="MidnightBlue" h="90px">
        <Header />
      </Box>
      <Box w="100%" bg="#f9f6ee" minH="calc(100vh - 90px)">
        <Flex>
          <SideBar />
          <Box bg="#fefefa" flex="1" padding={4} color="MidnightBlue">
            {props.routes}
          </Box>
        </Flex>
      </Box>
    </>
  );
};
