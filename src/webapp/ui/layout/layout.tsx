import { Box, ColorModeProvider, CSSReset, Flex } from "@chakra-ui/react";
import { useLocation } from "react-router-dom";
import { Header } from "./header";
import { SideBar } from "./sidebar";

type LayoutProps = {
  routes: React.ReactNode;
};

export const Layout: React.FunctionComponent<LayoutProps> = (
  props: LayoutProps
) => {
  const location = useLocation();
  if (location.pathname.startsWith("/admin/pages/preview")) {
    return <>{props.routes}</>;
  }
  return (
    <>
      <Box w="100%" p={4} bg="teal.300" h="90px">
        <Header />
      </Box>
      <Box w="100%" bg="teal.50" minH="calc(100vh - 90px)" color="teal.900">
        <Flex>
          <SideBar />
          <Box flex="1" padding={4}>
            {props.routes}
          </Box>
        </Flex>
      </Box>
    </>
  );
};
